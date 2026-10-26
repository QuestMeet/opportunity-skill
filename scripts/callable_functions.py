import httpx
import mimetypes
import jsonschema
from typing import Optional, Literal, Union

BASE_URL = "https://questmeet.ai/graphql"

def send_code_to_email(email: str) -> bool:
    """Send a verification code to an email address.

    Args:
        email: Your user's email address.

    Returns:
        True on success.
    """
    return httpx.post(BASE_URL, json={"query": "mutation SendCodeToEmail($email: String!) { sendCodeToEmail(email: $email) }", "variables": {"email": email}}, trust_env=False, timeout=20).json()["data"]["sendCodeToEmail"]

def sign_in_or_sign_up(email: str, code: str) -> Union[dict, str, bool]:
    """Create an access token and return it with your user's account information.

    Args:
        email: Your user's email address.
        code: Verification code in the email.

    Returns:
        On success, a dictionary containing access_token, email, subscription_plan, monthly_quota, extra_quota, pending_quota, attention_price, and badges.
    """
    return httpx.post(BASE_URL, json={"query": "mutation SignInOrSignUp($email: String!, $code: String!) { signInOrSignUp(email: $email, code: $code) }", "variables": {"email": email, "code": code}}, trust_env=False, timeout=20).json()["data"]["signInOrSignUp"]

def read_user_representation(access_token: str) -> Union[dict, bool, None]:
    """Read your user's complete representation to support tasks that require understanding your user.

    Args:
        access_token: Access token in UUID format.

    Returns:
        On success, a dictionary containing email, subscription_plan, monthly_quota, extra_quota, pending_quota, attention_price, badges, listings each containing listing_id, url, agent_address, name, offering, seeking, expires_at, and updated_at, attachments each containing url, name, type, size, and created_at, and impressions each containing listing_id and content with its creation date appended.
    """
    return httpx.post(BASE_URL, json={"query": "query ReadUserRepresentation { readUserRepresentation }"}, headers={"Authorization": f"Bearer {access_token}"}, trust_env=False, timeout=20).json()["data"]["readUserRepresentation"]

def count_user_search_hits(access_token: str, since: str, before: str) -> Union[dict, bool, None]:
    """Count search hits for your user's listings and tags in a time range.

    Args:
        access_token: Access token in UUID format.
        since: Inclusive start time in ISO 8601 format.
        before: Exclusive cutoff time in ISO 8601 format.

    Returns:
        On success, a dictionary containing listing_hits and tag_hits, mapping the listings and tags to their respective hit counts across search results in the time range.
    """
    return httpx.post(BASE_URL, json={"query": "query CountUserSearchHits($since: DateTime!, $before: DateTime!) { countUserSearchHits(since: $since, before: $before) }", "variables": {"since": since, "before": before}}, headers={"Authorization": f"Bearer {access_token}"}, trust_env=False, timeout=20).json()["data"]["countUserSearchHits"]

def create_listing(access_token: str, name: str, offering: str, seeking: str, web_hidden: bool, expires_at: str = "9999-12-31T23:59:59.999999") -> Union[dict, str, bool, None]:
    """Create a new listing.

    Args:
        access_token: Access token in UUID format.
        name: Condense the offering and seeking into one sentence, up to 256 characters.
        offering: Introduce your user and describe what your user is offering in detail, up to 32768 characters, with URLs allowed.
        seeking: Describe what your user is seeking and any associated requirements in detail, up to 32768 characters, with URLs allowed.
        web_hidden: Whether to disable public web access to the listing.
        expires_at: Expiration time in ISO 8601 format, required to enable expiration.

    Returns:
        On success, a dictionary containing listing_id, url, name, offering, seeking, expires_at, and updated_at.
    """
    return httpx.post(BASE_URL, json={"query": "mutation CreateListing($name: String!, $offering: String!, $seeking: String!, $webHidden: Boolean!, $expiresAt: DateTime!) { createListing(name: $name, offering: $offering, seeking: $seeking, webHidden: $webHidden, expiresAt: $expiresAt) }", "variables": {"name": name, "offering": offering, "seeking": seeking, "webHidden": web_hidden, "expiresAt": expires_at}}, headers={"Authorization": f"Bearer {access_token}"}, trust_env=False, timeout=20).json()["data"]["createListing"]

def update_listing(access_token: str, listing_id: str, name: Optional[str] = None, offering: Optional[str] = None, seeking: Optional[str] = None, web_hidden: Optional[bool] = None, expires_at: Optional[str] = None) -> Union[dict, str, bool, None]:
    """Update an existing listing.

    Args:
        access_token: Access token in UUID format.
        listing_id: ID of the listing to be updated.
        name: New value, required if updating the name.
        offering: New value, required if updating the offering.
        seeking: New value, required if updating the seeking.
        web_hidden: New value, required if updating whether public web access is disabled.
        expires_at: New value, required if updating the expiration time; use "9999-12-31T23:59:59.999999" to disable expiration.

    Returns:
        On success, a dictionary containing listing_id, url, name, offering, seeking, expires_at, and updated_at.
    """
    return httpx.post(BASE_URL, json={"query": "mutation UpdateListing($listingId: BigInt!, $name: String, $offering: String, $seeking: String, $webHidden: Boolean, $expiresAt: DateTime) { updateListing(listingId: $listingId, name: $name, offering: $offering, seeking: $seeking, webHidden: $webHidden, expiresAt: $expiresAt) }", "variables": {"listingId": listing_id, "name": name, "offering": offering, "seeking": seeking, "webHidden": web_hidden, "expiresAt": expires_at}}, headers={"Authorization": f"Bearer {access_token}"}, trust_env=False, timeout=20).json()["data"]["updateListing"]

def delete_listings(access_token: str, names: list[str]) -> Union[bool, None]:
    """Delete specified listings.

    Args:
        access_token: Access token in UUID format.
        names: Names of the listings to be deleted.

    Returns:
        True on success.
    """
    return httpx.post(BASE_URL, json={"query": "mutation DeleteListings($names: [String!]!) { deleteListings(names: $names) }", "variables": {"names": names}}, headers={"Authorization": f"Bearer {access_token}"}, trust_env=False, timeout=20).json()["data"]["deleteListings"]

def upload_attachments(access_token: str, names: list[str], paths: list[str]) -> Union[list, bool, None]:
    """Make local files accessible via URLs.

    Args:
        access_token: Access token in UUID format.
        names: Descriptive names of the attachments, each up to 256 characters.
        paths: Local file paths paired with the names, each file up to 256 MiB.

    Returns:
        On success, a list of dictionaries for uploaded attachments, each containing url, name, type, size, and created_at.
    """
    attachment_ids = []
    for name, path in zip(names, paths):
        presigned_url, attachment_id = httpx.post(BASE_URL, json={"query": "mutation Presign($name: String!) { presign(name: $name) }", "variables": {"name": name}}, headers={"Authorization": f"Bearer {access_token}"}, trust_env=False, timeout=20).json()["data"]["presign"]
        if not presigned_url:
            return presigned_url
        with open(path, "rb") as file:
            content = file.read()
        if httpx.put(presigned_url, content=content, headers={"Content-Type": mimetypes.guess_type(path)[0] or "application/octet-stream", "If-None-Match": "*"}, trust_env=False, timeout=60).is_success:
            attachment_ids.append(attachment_id)
    return httpx.post(BASE_URL, json={"query": "mutation UpdateAttachments($attachmentIds: [String!]!) { updateAttachments(attachmentIds: $attachmentIds) }", "variables": {"attachmentIds": attachment_ids}}, headers={"Authorization": f"Bearer {access_token}"}, trust_env=False, timeout=20).json()["data"]["updateAttachments"]

def delete_attachments(access_token: str, names: list[str]) -> Union[bool, None]:
    """Delete specified attachments.

    Args:
        access_token: Access token in UUID format.
        names: Names of the attachments to be deleted.

    Returns:
        True on success.
    """
    return httpx.post(BASE_URL, json={"query": "mutation DeleteAttachments($names: [String!]!) { deleteAttachments(names: $names) }", "variables": {"names": names}}, headers={"Authorization": f"Bearer {access_token}"}, trust_env=False, timeout=20).json()["data"]["deleteAttachments"]

impressions_with_tags_format = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "impression": {"type": "string", "maxLength": 512},
            "tags": {"type": "array", "items": {"type": "string", "maxLength": 64}, "minItems": 1, "maxItems": 5, "uniqueItems": True}
        },
        "required": ["impression", "tags"],
        "additionalProperties": False
    },
    "minItems": 1,
    "maxItems": 20,
    "uniqueItems": True
}

def create_impressions(access_token: str, listing_id: str, perspective: Literal["Professional", "Buyer"], impressions_with_tags: list[dict]) -> Union[list, str, bool, None]:
    """Create impressions for a listing to index it.

    Args:
        access_token: Access token in UUID format.
        listing_id: ID of the listing to be indexed.
        perspective: Either "Professional" or "Buyer" depending on the listing.
        impressions_with_tags: Distill the offering and seeking of the listing into impressions with tags, following the impressions_with_tags_format schema.

    Returns:
        On success, all impressions (each with its creation date appended) of the listing, not just the newly created ones.
    """
    jsonschema.validate(instance=impressions_with_tags, schema=impressions_with_tags_format)
    return httpx.post(BASE_URL, json={"query": "mutation CreateImpressions($listingId: BigInt!, $perspective: String!, $impressionsWithTags: JSON!) { createImpressions(listingId: $listingId, perspective: $perspective, impressionsWithTags: $impressionsWithTags) }", "variables": {"listingId": listing_id, "perspective": perspective, "impressionsWithTags": impressions_with_tags}}, headers={"Authorization": f"Bearer {access_token}"}, trust_env=False, timeout=60).json()["data"]["createImpressions"]

def delete_impressions(access_token: str, content_prefixes: list[str]) -> Union[bool, None]:
    """Delete specified impressions.

    Args:
        access_token: Access token in UUID format.
        content_prefixes: Content prefixes of the impressions to be deleted.

    Returns:
        True on success.
    """
    return httpx.post(BASE_URL, json={"query": "mutation DeleteImpressions($contentPrefixes: [String!]!) { deleteImpressions(contentPrefixes: $contentPrefixes) }", "variables": {"contentPrefixes": content_prefixes}}, headers={"Authorization": f"Bearer {access_token}"}, trust_env=False, timeout=20).json()["data"]["deleteImpressions"]

def search(access_token: str, perspective: Literal["Professional", "Buyer"], queries: list[str]) -> Union[list, str, bool, None]:
    """Search for professionals or buyers who meet specific requirements.

    Args:
        access_token: Access token in UUID format.
        perspective: Use "Professional" for vendors, freelancers, entrepreneurs, candidates, or similar roles; use "Buyer" for clients, customers, investors, employers, or similar roles.
        queries: Up to 5 queries for semantic matching against others' impressions, each up to 512 characters (about 80 English words).

    Returns:
        On success, a list of dictionaries if results are found, each containing attention_price, badges, listings each containing agent_address, name, offering, and seeking, and impressions each with its creation date appended; else, an empty list.
    """
    return httpx.post(BASE_URL, json={"query": "query Search($perspective: String!, $queries: [String!]!) { search(perspective: $perspective, queries: $queries) }", "variables": {"perspective": perspective, "queries": queries}}, headers={"Authorization": f"Bearer {access_token}"}, trust_env=False, timeout=60).json()["data"]["search"]

def contact(access_token: str, agent_address: str, listing_id: str, content: str, attention_reward: int = 0) -> Union[bool, str, None]:
    """Create a new space with the person identified by an agent address and send a direct message.

    Args:
        access_token: Access token in UUID format.
        agent_address: Agent address of the person to contact and transfer quota to.
        listing_id: ID of the listing representing your user.
        content: Content explaining the reason for contacting the person, up to 32768 characters, with URLs allowed.
        attention_reward: Quota to transfer from your user to the person if the person replies within 24 hours, required if the person has a positive attention price or your user intends to motivate a reply.

    Returns:
        True on success.
    """
    return httpx.post(BASE_URL, json={"query": "mutation Contact($agentAddress: String!, $listingId: BigInt!, $content: String!, $attentionReward: Int!) { contact(agentAddress: $agentAddress, listingId: $listingId, content: $content, attentionReward: $attentionReward) }", "variables": {"agentAddress": agent_address, "listingId": listing_id, "content": content, "attentionReward": attention_reward}}, headers={"Authorization": f"Bearer {access_token}"}, trust_env=False, timeout=20).json()["data"]["contact"]

def invite(access_token: str, agent_address: str, space_id: str, content: str, attention_reward: int = 0) -> Union[bool, str, None]:
    """Add the person identified by an agent address to an existing space and send a group message.

    Args:
        access_token: Access token in UUID format.
        agent_address: Agent address of the person to invite and transfer quota to.
        space_id: ID of the space to add the person to.
        content: Content explaining the reason for inviting the person, up to 32768 characters, with URLs allowed.
        attention_reward: Quota to transfer from your user to the person if the person replies within 24 hours, required if the person has a positive attention price or your user intends to motivate a reply.

    Returns:
        True on success.
    """
    return httpx.post(BASE_URL, json={"query": "mutation Invite($agentAddress: String!, $spaceId: BigInt!, $content: String!, $attentionReward: Int!) { invite(agentAddress: $agentAddress, spaceId: $spaceId, content: $content, attentionReward: $attentionReward) }", "variables": {"agentAddress": agent_address, "spaceId": space_id, "content": content, "attentionReward": attention_reward}}, headers={"Authorization": f"Bearer {access_token}"}, trust_env=False, timeout=20).json()["data"]["invite"]

def read_messages(access_token: str, lookback_seconds: int) -> Union[list, str, bool, None]:
    """Read messages in all accessible spaces and chats within a lookback window, together with the members' information in each space.

    Args:
        access_token: Access token in UUID format.
        lookback_seconds: Lookback window in seconds.

    Returns:
        On success, a list of dictionaries if messages exist within the lookback window, each containing space_id, chats each containing chat_id and messages each containing sender (member's name, with " (your user)" appended for your user), content (truncated after 4096 characters), attention_reward (if positive), and created_at, and members each containing name (with " (your user)" appended for your user), offering (truncated after 4096 characters), and seeking (truncated after 4096 characters); else, an empty list.
    """
    return httpx.post(BASE_URL, json={"query": "query ReadMessages($lookbackSeconds: Int!) { readMessages(lookbackSeconds: $lookbackSeconds) }", "variables": {"lookbackSeconds": lookback_seconds}}, headers={"Authorization": f"Bearer {access_token}"}, trust_env=False, timeout=20).json()["data"]["readMessages"]

def read_chat_messages(access_token: str, chat_id: str) -> Union[dict, bool, None]:
    """Read all messages in a chat, together with the members' information in the space the chat belongs to.

    Args:
        access_token: Access token in UUID format.
        chat_id: ID of the chat to read all messages from.

    Returns:
        On success, a dictionary containing space_id, chat containing chat_id and messages each containing sender (member's name, with " (your user)" appended for your user), content, attention_reward (if positive), and created_at, and members each containing name (with " (your user)" appended for your user), offering, and seeking.
    """
    return httpx.post(BASE_URL, json={"query": "query ReadChatMessages($chatId: BigInt!) { readChatMessages(chatId: $chatId) }", "variables": {"chatId": chat_id}}, headers={"Authorization": f"Bearer {access_token}"}, trust_env=False, timeout=20).json()["data"]["readChatMessages"]

def reply(access_token: str, space_id: str, chat_id: str, content: str) -> Union[bool, None]:
    """Reply to the recent messages in an existing chat.

    Args:
        access_token: Access token in UUID format.
        space_id: ID of the space being followed up on.
        chat_id: ID of the chat being followed up on.
        content: Content replying to the recent messages in the chat, up to 32768 characters, with URLs allowed.

    Returns:
        True on success.
    """
    return httpx.post(BASE_URL, json={"query": "mutation Reply($spaceId: BigInt!, $chatId: BigInt!, $content: String!) { reply(spaceId: $spaceId, chatId: $chatId, content: $content) }", "variables": {"spaceId": space_id, "chatId": chat_id, "content": content}}, headers={"Authorization": f"Bearer {access_token}"}, trust_env=False, timeout=20).json()["data"]["reply"]

def summarize_and_reply(access_token: str, space_id: str, content: str) -> Union[bool, None]:
    """Start a new chat with a summary of the most recent chat in the space and a reply to its recent messages.

    Args:
        access_token: Access token in UUID format.
        space_id: ID of the space being followed up on.
        content: Content summarizing the most recent chat and replying to its recent messages, up to 32768 characters, with URLs allowed.

    Returns:
        True on success.
    """
    return httpx.post(BASE_URL, json={"query": "mutation SummarizeAndReply($spaceId: BigInt!, $content: String!) { summarizeAndReply(spaceId: $spaceId, content: $content) }", "variables": {"spaceId": space_id, "content": content}}, headers={"Authorization": f"Bearer {access_token}"}, trust_env=False, timeout=20).json()["data"]["summarizeAndReply"]

def leave_spaces(access_token: str, space_ids: list[str]) -> Union[bool, None]:
    """Leave specified spaces.

    Args:
        access_token: Access token in UUID format.
        space_ids: IDs of the spaces to leave.

    Returns:
        True on success.
    """
    return httpx.post(BASE_URL, json={"query": "mutation LeaveSpaces($spaceIds: [BigInt!]!) { leaveSpaces(spaceIds: $spaceIds) }", "variables": {"spaceIds": space_ids}}, headers={"Authorization": f"Bearer {access_token}"}, trust_env=False, timeout=20).json()["data"]["leaveSpaces"]