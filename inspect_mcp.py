import asyncio

from fastmcp import FastMCP

mcp = FastMCP("test")


async def inspect():
    print(f"Attributes: {dir(mcp)}")
    if hasattr(mcp, "custom_route"):
        print(f"mcp.custom_route: {mcp.custom_route}")
    else:
        print("No custom_route attribute found")

    # Try to get ASGI app
    try:
        asgi = mcp.as_asgi_app()
        print(f"ASGI App: {asgi}")
        print(f"ASGI Dir: {dir(asgi)}")
    except Exception as e:
        print(f"as_asgi_app failed: {e}")


if __name__ == "__main__":
    asyncio.run(inspect())
