import os
import re
import time
import base64
import mimetypes
import pathlib
from typing import List, Dict, Any, Optional

from PIL import Image
from google import genai

# =========================================
# Configuration
# =========================================
BASE_DIR = pathlib.Path(__file__).resolve().parent
INPUT_DIR = str(BASE_DIR / "manga")        # Original manga images
FINAL_DIR = str(BASE_DIR / "manga_out")    # Folder to collect best images
OUT_PREFIX = "out"                         # out1, out2, out3, ...
BATCH_SIZE = 1000                             # How many pages to compare per ranking batch
BEST_LOG_PATH = str(BASE_DIR / "manga_best_k.tsv")

API_KEY = ""  # or use GEMINI_API_KEY / GOOGLE_API_KEY from env
MAX_RANK_RETRIES = 3                       # How many times to retry ranking when model / k값 문제가 있을 때

# =========================================
# Helpers
# =========================================
PAREN_SUFFIX_RE = re.compile(r"\s*\([^()]*\)$")


def natural_key(s: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def strip_trailing_paren_suffix(stem: str) -> str:
    return PAREN_SUFFIX_RE.sub("", stem)


def normalized_base_from_filename(filename: str) -> str:
    stem = pathlib.Path(filename).stem
    return strip_trailing_paren_suffix(stem)


def list_images(folder: str) -> List[str]:
    exts = {".png", ".jpg", ".jpeg", ".webp"}
    try:
        files = [f for f in os.listdir(folder) if pathlib.Path(f).suffix.lower() in exts]
    except FileNotFoundError:
        return []
    return sorted(files, key=natural_key)


def image_part_dict(path: str) -> Dict[str, Any]:
    mt = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as f:
        raw = f.read()
    b64 = base64.b64encode(raw).decode("ascii")
    return {"inline_data": {"mime_type": mt, "data": b64}}


def extract_first_text(resp_obj) -> Optional[str]:
    candidates = getattr(resp_obj, "candidates", None) or []
    for cand in candidates:
        content = getattr(cand, "content", None)
        if not content:
            continue
        parts = getattr(content, "parts", None) or []
        texts: List[str] = []
        for part in parts:
            text = getattr(part, "text", None)
            if text:
                texts.append(text)
        if texts:
            return "".join(texts).strip()
    return None


# =========================================
# Ranking prompt (original + multiple candidates)
# =========================================
RANK_PROMPT = r"""
You are an evaluator model.

You will receive:
- One ORIGINAL manga page image containing the Japanese text and the original artwork.
- Several CANDIDATE images that are supposed to be the translated versions of that same page.

Your job is to choose exactly one best candidate according to the following priority rules:

Priority 1: Do NOT create a new manga page.
- Reject any candidate that clearly redraws or re-stages the scene.
- If a candidate adds new panels, changes panel borders, drastically changes character poses or camera angles, or turns the page into a different composition, you must treat that candidate as much worse than any candidate that preserves the original layout.

Priority 2: Forbid true vertical Korean writing.
- All Korean text must be left-to-right horizontal.
- It is allowed to break one Korean sentence into two or more horizontal lines stacked vertically inside the same bubble. For example:
    first line: "천박한"
    second line: "것이."
  This is still horizontal Korean, because each individual line is left-to-right.
- It is strictly forbidden to write a single Korean word with each syllable block under the previous one in a straight vertical column, for example:

  천
  박
  한

  This is vertical Korean and must be considered wrong.

Priority 3: Translation and guideline quality.
- Prefer candidates where:
  - all visible Japanese or English text has been translated into natural Korean,
  - Korean is placed inside the correct bubbles and text areas,
  - the overall panel layout and artwork are preserved as closely as possible,
  - sound effects (SFX) are localized into natural Korean where appropriate,
  - tone, character voice, and nuance are consistent with the original as far as you can infer.

Decision rule:
- Consider all candidates together.
- First, eliminate or strongly down-rank any candidate that violates Priority 1 (new manga page) or Priority 2 (true vertical Korean).
- Among the remaining candidates, choose the one that best satisfies Priority 3.
- If all candidates have some issues, still choose the one that is the least bad according to these priorities.

Output format:
On the first line, write exactly:

BEST: k

where k is the 1-based index of the best candidate image among the candidates you see (CANDIDATE_1, CANDIDATE_2, ...).

After that, you may optionally write a short explanation on the following lines, but the first line MUST be in the format "BEST: k".
"""


def try_parse_best_index(text: str, num_candidates: int) -> Optional[int]:
    """
    Try to parse "BEST: k" from the first non-empty line.
    Returns k (1..num_candidates) on success, or None on failure.
    """
    if not text:
        return None
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return None
    first = lines[0]
    m = re.search(r"BEST\s*:\s*(\d+)", first, re.IGNORECASE)
    if not m:
        # try to find any integer 1..num_candidates as a fallback
        m2 = re.search(r"\b([1-9]\d*)\b", first)
        if not m2:
            return None
        k = int(m2.group(1))
        if 1 <= k <= num_candidates:
            return k
        return None
    k = int(m.group(1))
    if 1 <= k <= num_candidates:
        return k
    return None


def ensure_best_log_header():
    """
    Ensure BEST_LOG_PATH exists and has a header line.
    """
    if not os.path.isfile(BEST_LOG_PATH):
        with open(BEST_LOG_PATH, "w", encoding="utf-8") as f:
            f.write("base_name\tbest_index\tcandidate_folder\tcandidate_filename\n")


# =========================================
# Folder helpers
# =========================================
def find_out_folders() -> List[str]:
    """
    Find all outN folders (out1, out2, ...) under BASE_DIR and return their paths sorted by N.
    """
    folders = []
    for name in os.listdir(BASE_DIR):
        m = re.fullmatch(rf"{OUT_PREFIX}(\d+)", name)
        if not m:
            continue
        num = int(m.group(1))
        path = os.path.join(BASE_DIR, name)
        if os.path.isdir(path):
            folders.append((num, path))
    folders.sort(key=lambda x: x[0])
    return [p for _, p in folders]


def build_folder_index(folder: str) -> Dict[str, str]:
    """
    Map base_name -> file_path for one outN folder.
    """
    idx: Dict[str, str] = {}
    for fname in list_images(folder):
        base = normalized_base_from_filename(fname)
        idx[base] = os.path.join(folder, fname)
    return idx


# =========================================
# Main logic
# =========================================
def main():
    # API key
    api_key = API_KEY or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
    if not api_key:
        raise RuntimeError("API key not found. Set API_KEY or GEMINI_API_KEY/GOOGLE_API_KEY.")

    # Input check
    if not os.path.isdir(INPUT_DIR):
        raise RuntimeError(f"Input directory not found: {INPUT_DIR}")
    orig_files = list_images(INPUT_DIR)
    if not orig_files:
        raise RuntimeError(f"No images found in input directory: {INPUT_DIR}")

    base_to_orig: Dict[str, str] = {}
    for img in orig_files:
        base = normalized_base_from_filename(img)
        base_to_orig[base] = os.path.join(INPUT_DIR, img)
    all_bases = sorted(base_to_orig.keys(), key=natural_key)
    print(f"Found {len(all_bases)} base page(s) in {INPUT_DIR}.")

    # Find outN folders
    out_folders = find_out_folders()
    if not out_folders:
        raise RuntimeError("No outN folders found (e.g., out1, out2, out3...). Nothing to compare.")
    print("Detected output folders (in order):")
    for f in out_folders:
        print(" -", os.path.basename(f))

    # Build indices for each outN
    folder_indices: List[Dict[str, str]] = []
    for f in out_folders:
        idx = build_folder_index(f)
        folder_indices.append(idx)
        print(f"Folder {os.path.basename(f)} has {len(idx)} image(s).")

    # Prepare final folder
    os.makedirs(FINAL_DIR, exist_ok=True)

    # Ensure BEST log header
    ensure_best_log_header()

    # Init client
    client_text = genai.Client(api_key=api_key, http_options={"api_version": "v1alpha"})

    # Collect bases that need model ranking (>=2 candidates)
    bases_need_rank = []
    base_to_candidates: Dict[str, List[str]] = {}

    for base in all_bases:
        candidates: List[str] = []
        for idx in folder_indices:
            path = idx.get(base)
            if path and os.path.isfile(path):
                candidates.append(path)
        if not candidates:
            print(f"[WARN] No candidates found for base {base}. Skipping.")
            continue

        if len(candidates) == 1:
            # Single candidate: just copy it as the best
            src = candidates[0]
            dst = os.path.join(FINAL_DIR, f"{base}.jpg")
            try:
                img = Image.open(src).convert("RGB")
                img.save(dst, format="JPEG", quality=95)
                print(f"[COPY-ONLY] {base}: only 1 candidate, copied to manga_out.")

                cand_folder = os.path.basename(os.path.dirname(src))
                cand_file = os.path.basename(src)
                with open(BEST_LOG_PATH, "a", encoding="utf-8") as lf:
                    lf.write(f"{base}\t1\t{cand_folder}\t{cand_file}\n")
            except Exception as e:
                print(f"[WARN] Failed to copy-only {base}: {e}")
            continue

        # Need ranking
        base_to_candidates[base] = candidates
        bases_need_rank.append(base)

    print(f"\nTotal pages needing ranking: {len(bases_need_rank)}")

    # Ranking in batches
    start = 0
    while start < len(bases_need_rank):
        chunk_bases = bases_need_rank[start : start + BATCH_SIZE]
        start += BATCH_SIZE
        print(f"\nRanking batch with {len(chunk_bases)} page(s): {chunk_bases}")

        # We will try up to MAX_RANK_RETRIES for this chunk
        pending_bases = list(chunk_bases)
        best_index_map: Dict[str, int] = {}
        attempt = 0

        while pending_bases and attempt < MAX_RANK_RETRIES:
            attempt += 1
            print(f"[RANK] Attempt {attempt} for {len(pending_bases)} pending page(s).")

            inline_requests = []
            base_order: List[str] = []

            for base in pending_bases:
                orig_path = base_to_orig[base]
                candidates = base_to_candidates[base]
                contents = [
                    {
                        "role": "user",
                        "parts": [
                            {"text": RANK_PROMPT},
                            {"text": "<ORIGINAL_IMAGE>"},
                            image_part_dict(orig_path),
                            {"text": "</ORIGINAL_IMAGE>"},
                        ],
                    }
                ]

                # Add candidates
                for i, cand_path in enumerate(candidates, start=1):
                    contents[0]["parts"].append({"text": f"<CANDIDATE_{i}>"})
                    contents[0]["parts"].append(image_part_dict(cand_path))
                    contents[0]["parts"].append({"text": f"</CANDIDATE_{i}>"})

                inline_requests.append(
                    {
                        "contents": contents,
                        "config": {"response_modalities": ["TEXT"]},
                    }
                )
                base_order.append(base)

            if not inline_requests:
                break

            try:
                job = client_text.batches.create(
                    model="models/gemini-3-pro-preview",
                    src=inline_requests,
                    config={"display_name": f"manga-best-selector-attempt-{attempt}"},
                )
            except Exception as e:
                print(f"[ERROR] Failed to create ranking batch (attempt {attempt}): {e}")
                time.sleep(5)
                continue

            # Poll
            job_done = None
            while True:
                status = client_text.batches.get(name=job.name)
                state = status.state.name
                if state in {
                    "JOB_STATE_SUCCEEDED",
                    "JOB_STATE_FAILED",
                    "JOB_STATE_CANCELLED",
                    "JOB_STATE_EXPIRED",
                }:
                    job_done = status
                    break
                print(f"  - Ranking batch status: {state} (polling...)")
                time.sleep(10)

            if not job_done or job_done.state.name != "JOB_STATE_SUCCEEDED":
                err_state = job_done.state.name if job_done else "Unknown"
                print(f"[ERROR] Ranking batch ended with state: {err_state}")
                time.sleep(5)
                continue

            inline_responses = (job_done.dest.inlined_responses or []) if job_done.dest else []
            if not inline_responses:
                print("[WARN] No inline responses from ranking batch.")
                time.sleep(5)
                continue

            # Process responses
            newly_solved = []
            for base, inline_resp in zip(base_order, inline_responses):
                if base not in pending_bases:
                    continue
                cands = base_to_candidates[base]

                if not inline_resp.response:
                    print(f"[WARN] No ranking response for {base} on attempt {attempt}.")
                    continue

                raw_text = extract_first_text(inline_resp.response)
                best_idx = try_parse_best_index(raw_text, len(cands))
                if best_idx is None:
                    print(f"[WARN] Could not parse BEST index for {base} on attempt {attempt}. Raw first line may be malformed.")
                    continue

                best_index_map[base] = best_idx
                newly_solved.append(base)
                print(f"[RANK-OK] {base}: BEST = {best_idx} (attempt {attempt})")

            # Remove solved bases from pending_bases
            pending_bases = [b for b in pending_bases if b not in newly_solved]

        # After retries, finalize results (use fallback if needed)
        for base in chunk_bases:
            candidates = base_to_candidates[base]
            if not candidates:
                print(f"[WARN] No candidates for {base} at finalize stage.")
                continue

            if base in best_index_map:
                best_idx = best_index_map[base]
            else:
                # Fallback: if ranking repeatedly failed or BEST를 못 받음 → 1번 후보
                best_idx = 1
                print(f"[FALLBACK] {base}: using candidate #1 after {MAX_RANK_RETRIES} failed attempts.")

            best_idx = max(1, min(best_idx, len(candidates)))
            best_path = candidates[best_idx - 1]
            dst = os.path.join(FINAL_DIR, f"{base}.jpg")

            try:
                img = Image.open(best_path).convert("RGB")
                img.save(dst, format="JPEG", quality=95)
                print(f"[BEST] {base}: selected candidate #{best_idx} from {os.path.dirname(best_path)}")

                cand_folder = os.path.basename(os.path.dirname(best_path))
                cand_file = os.path.basename(best_path)
                with open(BEST_LOG_PATH, "a", encoding="utf-8") as lf:
                    lf.write(f"{base}\t{best_idx}\t{cand_folder}\t{cand_file}\n")
            except Exception as e:
                print(f"[WARN] Failed to save best for {base}: {e}")
                # Last fallback: try first candidate
                try:
                    img = Image.open(candidates[0]).convert("RGB")
                    img.save(dst, format="JPEG", quality=95)
                    print(f"[FALLBACK-FIRST] {base}: saved first candidate.")

                    cand_folder = os.path.basename(os.path.dirname(candidates[0]))
                    cand_file = os.path.basename(candidates[0])
                    with open(BEST_LOG_PATH, "a", encoding="utf-8") as lf:
                        lf.write(f"{base}\t1\t{cand_folder}\t{cand_file}\n")
                except Exception as e2:
                    print(f"[WARN] Fallback failed for {base}: {e2}")

    try:
        client_text.close()
    except Exception:
        pass

    print(f"\nDone. Best images collected into: {FINAL_DIR}")
    print(f"Best index log written to: {BEST_LOG_PATH}")


if __name__ == "__main__":
    main()
