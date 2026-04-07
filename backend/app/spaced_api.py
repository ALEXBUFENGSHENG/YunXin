from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from .spaced_memory import SpacedRepetitionScheduler, initialize_database

initialize_database()
scheduler = SpacedRepetitionScheduler()
router = APIRouter(prefix="/api/memory", tags=["memory"])

class ReviewRequest(BaseModel):
    user_id: int
    word_id: int
    score: int  # 0-5
    interaction_type: str = "choice"
    response_time_ms: Optional[int] = None

class WordResponse(BaseModel):
    word_id: int
    word: str
    pronunciation: Optional[str] = None
    definition: Optional[str] = None
    example_sentence: Optional[str] = None
    roots: Optional[str] = None
    is_new: bool = False

@router.post("/review")
async def record_review(req: ReviewRequest):
    try:
        scheduler.record_review(
            user_id=req.user_id,
            word_id=req.word_id,
            score=req.score,
            interaction_type=req.interaction_type,
            response_time_ms=req.response_time_ms,
        )
        return {"message": "review recorded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/today/{user_id}")
async def get_today_words(user_id: int, limit: int = 15) -> List[WordResponse]:
    print(f"DEBUG: get_today_words called for user_id={user_id}")
    try:
        words = scheduler.get_today_review_queue(user_id, limit)
        print(f"DEBUG: get_today_review_queue returned {len(words)} words")
        
        # 若不足则补新词
        if len(words) < max(3, limit // 2):
            need = limit - len(words)
            print(f"DEBUG: Need {need} more words")
            new_ids = scheduler.get_new_word_ids(user_id, need)
            print(f"DEBUG: Found {len(new_ids)} new word ids: {new_ids}")
            if new_ids:
                scheduler.add_new_words_to_user(user_id, new_ids)
                print("DEBUG: Added new words to user")
                words = scheduler.get_today_review_queue(user_id, limit)
                print(f"DEBUG: Refetched words, now have {len(words)}")
        
        resp = []
        for w in words:
            # Ensure word_id is present
            if 'word_id' not in w:
                print(f"ERROR: Missing word_id in word: {w}")
                # Try to use 'id' if available
                if 'id' in w:
                    w['word_id'] = w['id']
                else:
                    continue

            resp.append(WordResponse(
                word_id=w['word_id'],
                word=w['word'],
                pronunciation=w.get('pronunciation'),
                definition=w.get('definition'),
                example_sentence=w.get('example_sentence'),
                roots=w.get('roots'),
                is_new=(w.get('review_count', 0) == 0)
            ))
        return resp
    except Exception as e:
        print(f"ERROR in get_today_words: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/progress/{user_id}")
async def get_progress(user_id: int):
    return scheduler.get_user_progress(user_id)
