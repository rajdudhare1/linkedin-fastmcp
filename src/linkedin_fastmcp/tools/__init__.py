from fastmcp import FastMCP

from linkedin_fastmcp.tools.api import register_api_tools
from linkedin_fastmcp.tools.auth import register_auth_tools
from linkedin_fastmcp.tools.comments import register_comment_tools
from linkedin_fastmcp.tools.events import register_event_tools
from linkedin_fastmcp.tools.media import register_media_tools
from linkedin_fastmcp.tools.organizations import register_organization_tools
from linkedin_fastmcp.tools.posts import register_post_tools
from linkedin_fastmcp.tools.profile import register_profile_tools
from linkedin_fastmcp.tools.reactions import register_reaction_tools


def register_tools(mcp: FastMCP) -> None:
    register_auth_tools(mcp)
    register_profile_tools(mcp)
    register_post_tools(mcp)
    register_comment_tools(mcp)
    register_reaction_tools(mcp)
    register_organization_tools(mcp)
    register_event_tools(mcp)
    register_media_tools(mcp)
    register_api_tools(mcp)
