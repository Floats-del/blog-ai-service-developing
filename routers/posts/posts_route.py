from fastapi import Request, Response, status, Depends, APIRouter
from core.exceptions import PostServiceException
from db import get_db
from typing import List, Optional
from routers.posts.posting_services import create_comment_service, create_post_service, delete_commentById_service, delete_post_by_id_service, fetch_post_by_id_service, get_Nposts_service, get_post_comments_service, update_post_by_id_service
from utils.ai_responce_handler import handle_service_response
from utils.schemas import PostLikesOutSchema, PostResponseSchema, PostCreateSchema
from Oauth2 import get_user_jwt_payload
from utils.schemas import APIResponse
from sqlalchemy.ext.asyncio import AsyncSession
from utils.schemas import CommentCreateSchema, CommentResponseSchema
from core.rate_limiters.limiter_file import limiter
from core.rate_limiters.limiter_utils import RateLimits




#currently no need for gatway since i only check db and jwt and i need them in routes so itd be pointless
router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)



@router.get("/get_all_posts", response_model=List[PostLikesOutSchema])
@limiter.limit(RateLimits.Posts.READ)
async def get_all_posts(request: Request, response: Response, db: AsyncSession = Depends(get_db), user_payload = Depends(get_user_jwt_payload), limit: int = 10, offset: int = 0, search: Optional[str] = None, personal_only: bool = False) -> List[PostLikesOutSchema]:
    result: APIResponse = await get_Nposts_service(user_payload=user_payload, db=db, limit=limit, search=search, offset=offset, personal_only=personal_only)
    return handle_service_response(result, PostServiceException) #either i get reult of PostServiceException




@router.post("/create_new_post", response_model=PostResponseSchema) 
@limiter.limit(RateLimits.Posts.WRITE)
async def create_post(request: Request, response: Response, new_post: PostCreateSchema,  user_payload = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)) -> PostResponseSchema:
    result: APIResponse = await create_post_service(user_payload=user_payload, db=db, new_post=new_post)
    return handle_service_response(result, PostServiceException)



@router.get("/get_post_by_id/{id}", response_model=PostLikesOutSchema)  
@limiter.limit(RateLimits.Posts.READ)
async def get_post_by_id(request: Request, response: Response, id: int, user_payload = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)) -> PostLikesOutSchema:  
    result: APIResponse = await fetch_post_by_id_service(user_payload=user_payload, db=db, id=id)
    return handle_service_response(result, PostServiceException)



@router.delete("/delete_post_by_id/{id}", status_code=status.HTTP_204_NO_CONTENT) 
@limiter.limit(RateLimits.Posts.DELETE)
async def delete_post_by_id(request: Request, response: Response, id: int, user_payload = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)):
    result: APIResponse = await delete_post_by_id_service(user_payload=user_payload, db=db, id=id)
    return handle_service_response(result, PostServiceException)





@router.put("/update_post_by_id/{id}", response_model=PostResponseSchema)
@limiter.limit(RateLimits.Posts.UPDATE)
async def update_by_id(request: Request, response: Response, id: int, post_data: PostCreateSchema, user_payload = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)):
    result: APIResponse = await update_post_by_id_service(user_payload=user_payload, db=db, id=id, post_data=post_data)
    return handle_service_response(result, PostServiceException)


@router.post("/add_a_comment_by_post_id/{post_id}/comment", status_code=status.HTTP_201_CREATED, response_model=CommentResponseSchema)
@limiter.limit(RateLimits.Comments.WRITE)
async def create_comment(request: Request, response: Response, post_id: int, comment_data: CommentCreateSchema, user_payload = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)) -> CommentResponseSchema:
    result: APIResponse = await create_comment_service(user_payload=user_payload, post_id=post_id, db=db, comment_data=comment_data)
    return handle_service_response(result, PostServiceException)





@router.get("/get_all_post_comment_by_post_id/{post_id}/comment", response_model=List[CommentResponseSchema])
@limiter.limit(RateLimits.Comments.READ)
async def get_comments_for_post(request: Request, response: Response, post_id: int, limit: int = 10, offset: int = 0, search: Optional[str] = None, db: AsyncSession = Depends(get_db), user_payload = Depends(get_user_jwt_payload)) -> List[CommentResponseSchema]: 
    result: APIResponse = await get_post_comments_service(user_payload, post_id=post_id, db=db, limit=limit, offset=offset, search=search)
    return handle_service_response(result, PostServiceException)




@router.delete("/delete_comment_by_post_id_and_comment_id/{post_id}/comment/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(RateLimits.Comments.DELETE)
async def delete_comment(request: Request, response: Response, post_id: int, comment_id: int, user_payload = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)):
    result: APIResponse = await delete_commentById_service(post_id=post_id, db=db, comment_id=comment_id, user_payload=user_payload)
    return handle_service_response(result, PostServiceException)