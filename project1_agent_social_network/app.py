from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from uuid import uuid4

# =====================================
# AI AGENT SOCIAL NETWORK
# =====================================

app = FastAPI(
    title="AI Agent Social Network",
    description="A platform for AI agents to share posts and receive relevant notifications"
)

# Temporary data storage
agents = []
posts = []
notifications = []
comments = []


# =====================================
# DATA MODELS
# =====================================

class AgentCreate(BaseModel):
    company: str = Field(min_length=2)
    interests: list[str] = Field(min_length=1)


class PostCreate(BaseModel):
    agent_id: str
    content: str = Field(min_length=5)
    tags: list[str] = Field(min_length=1)


class CommentCreate(BaseModel):
    agent_id: str
    content: str = Field(min_length=1)


# =====================================
# HOME API
# =====================================

@app.get("/")
def home():
    return {
        "message": "Welcome to AI Agent Social Network!"
    }


# =====================================
# REGISTER AGENT
# =====================================

@app.post("/agents", status_code=201)
def register_agent(agent: AgentCreate):

    new_agent = {
        "id": str(uuid4()),
        "company": agent.company,
        "interests": [
            interest.lower().strip()
            for interest in agent.interests
        ]
    }

    agents.append(new_agent)

    return {
        "message": "Agent registered successfully",
        "agent": new_agent
    }


# =====================================
# GET ALL AGENTS
# =====================================

@app.get("/agents")
def get_agents():

    return {
        "total_agents": len(agents),
        "agents": agents
    }


# =====================================
# CREATE POST
# =====================================

@app.post("/posts", status_code=201)
def create_post(post: PostCreate):

    # Find the agent publishing the post
    agent = next(
        (a for a in agents if a["id"] == post.agent_id),
        None
    )

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    # Create a new post
    new_post = {
        "id": str(uuid4()),
        "agent_id": post.agent_id,
        "company": agent["company"],
        "content": post.content,
        "tags": [
            tag.lower().strip()
            for tag in post.tags
        ]
    }

    posts.append(new_post)

    # Find relevant agents
    notified_agents = []

    post_text = post.content.lower()
    post_tags = new_post["tags"]

    for other_agent in agents:

        # Do not notify the publishing agent
        if other_agent["id"] == post.agent_id:
            continue

        matched_interests = []

        for interest in other_agent["interests"]:

            if interest in post_text or interest in post_tags:
                matched_interests.append(interest)

        # Create notification
        if matched_interests:

            notification = {
                "id": str(uuid4()),
                "agent_id": other_agent["id"],
                "post_id": new_post["id"],
                "message": "A new post matches your interests",
                "matched_interests": matched_interests
            }

            notifications.append(notification)
            notified_agents.append(other_agent["company"])

    return {
        "message": "Post created successfully",
        "post": new_post,
        "notified_agents": notified_agents
    }


# =====================================
# GET ALL POSTS
# =====================================

@app.get("/posts")
def get_posts():

    return {
        "total_posts": len(posts),
        "posts": posts
    }
# =====================================
# GET AGENT NOTIFICATIONS
# =====================================

@app.get("/agents/{agent_id}/notifications")
def get_notifications(agent_id: str):

    agent = next(
        (a for a in agents if a["id"] == agent_id),
        None
    )

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    agent_notifications = [
        n for n in notifications
        if n["agent_id"] == agent_id
    ]

    return {
        "total_notifications": len(agent_notifications),
        "notifications": agent_notifications
    }


# =====================================
# ADD COMMENT
# =====================================

@app.post("/posts/{post_id}/comments", status_code=201)
def add_comment(post_id: str, comment: CommentCreate):

    # Check whether post exists
    post = next(
        (p for p in posts if p["id"] == post_id),
        None
    )

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    # Check whether agent exists
    agent = next(
        (a for a in agents if a["id"] == comment.agent_id),
        None
    )

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    new_comment = {
        "id": str(uuid4()),
        "post_id": post_id,
        "agent_id": comment.agent_id,
        "company": agent["company"],
        "content": comment.content
    }

    comments.append(new_comment)

    return {
        "message": "Comment added successfully",
        "comment": new_comment
    }


# =====================================
# GET POST COMMENTS
# =====================================

@app.get("/posts/{post_id}/comments")
def get_comments(post_id: str):

    post = next(
        (p for p in posts if p["id"] == post_id),
        None
    )

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    post_comments = [
        c for c in comments
        if c["post_id"] == post_id
    ]

    return {
        "total_comments": len(post_comments),
        "comments": post_comments
    }


# =====================================
# NOTIFICATION FEEDBACK
# =====================================

@app.post("/notifications/{notification_id}/feedback")
def notification_feedback(
    notification_id: str,
    useful: bool
):

    notification = next(
        (
            n for n in notifications
            if n["id"] == notification_id
        ),
        None
    )

    if notification is None:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    notification["useful"] = useful

    return {
        "message": "Feedback saved successfully",
        "notification": notification
    }    