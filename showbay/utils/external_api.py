import httpx
import asyncio
import os
from typing import Dict, Any, Optional
from showbay.utils.exceptions import ExternalAPIException
from dotenv import load_dotenv

load_dotenv()

# External API configuration
EXTERNAL_API_BASE_URL = os.getenv("EXTERNAL_API_BASE_URL", "https://jsonplaceholder.typicode.com")
EXTERNAL_API_TIMEOUT = int(os.getenv("EXTERNAL_API_TIMEOUT", "10"))


async def fetch_external_data(external_id: int) -> Dict[str, Any]:
    """
    Fetch data from an external API.
    
    Args:
        external_id: ID to query in the external API
        
    Returns:
        Dict containing the external API response
        
    Raises:
        ExternalAPIException: If the external API request fails
    """
    try:
        # Construct the API URL - for JSONPlaceholder, we'll use posts endpoint
        url = f"{EXTERNAL_API_BASE_URL}/posts/{external_id}"
        
        # Make async request to external API
        async with httpx.AsyncClient(timeout=EXTERNAL_API_TIMEOUT) as client:
            response = await client.get(url)
            
            # Check if request was successful
            if response.status_code == 404:
                raise ExternalAPIException(
                    f"Resource with ID {external_id} not found in external API", 
                    status_code=404
                )
            elif response.status_code >= 400:
                raise ExternalAPIException(
                    f"External API request failed with status {response.status_code}: {response.text}",
                    status_code=response.status_code
                )
            
            # Return the JSON response
            return response.json()
            
    except httpx.TimeoutException:
        raise ExternalAPIException(
            f"Request to external API timed out after {EXTERNAL_API_TIMEOUT} seconds",
            status_code=408
        )
    except httpx.RequestError as e:
        raise ExternalAPIException(
            f"Request error when connecting to external API: {str(e)}",
            status_code=502
        )
    except Exception as e:
        raise ExternalAPIException(
            f"Unexpected error when fetching data from external API: {str(e)}",
            status_code=500
        )


async def create_external_resource(title: str, body: str, user_id: int = 1) -> Dict[str, Any]:
    """
    Create a resource in the external API.
    
    Args:
        title: Title for the new resource
        body: Body/content for the new resource
        user_id: User ID to associate with the resource
        
    Returns:
        Dict containing the external API response for the created resource
    """
    try:
        url = f"{EXTERNAL_API_BASE_URL}/posts"
        
        payload = {
            "title": title,
            "body": body,
            "userId": user_id
        }
        
        async with httpx.AsyncClient(timeout=EXTERNAL_API_TIMEOUT) as client:
            response = await client.post(url, json=payload)
            
            if response.status_code >= 400:
                raise ExternalAPIException(
                    f"External API create request failed with status {response.status_code}: {response.text}",
                    status_code=response.status_code
                )
                
            return response.json()
            
    except httpx.TimeoutException:
        raise ExternalAPIException(
            f"Request to external API timed out after {EXTERNAL_API_TIMEOUT} seconds",
            status_code=408
        )
    except httpx.RequestError as e:
        raise ExternalAPIException(
            f"Request error when connecting to external API: {str(e)}",
            status_code=502
        )
    except Exception as e:
        raise ExternalAPIException(
            f"Unexpected error when creating resource in external API: {str(e)}",
            status_code=500
        )


async def fetch_external_data_list(limit: int = 10) -> list[Dict[str, Any]]:
    """
    Fetch a list of resources from the external API.
    
    Args:
        limit: Maximum number of resources to fetch
        
    Returns:
        List of dictionaries containing external API responses
    """
    try:
        url = f"{EXTERNAL_API_BASE_URL}/posts"
        
        async with httpx.AsyncClient(timeout=EXTERNAL_API_TIMEOUT) as client:
            response = await client.get(url, params={"_limit": limit})
            
            if response.status_code >= 400:
                raise ExternalAPIException(
                    f"External API request failed with status {response.status_code}: {response.text}",
                    status_code=response.status_code
                )
                
            return response.json()
            
    except httpx.TimeoutException:
        raise ExternalAPIException(
            f"Request to external API timed out after {EXTERNAL_API_TIMEOUT} seconds",
            status_code=408
        )
    except httpx.RequestError as e:
        raise ExternalAPIException(
            f"Request error when connecting to external API: {str(e)}",
            status_code=502
        )
    except Exception as e:
        raise ExternalAPIException(
            f"Unexpected error when fetching data list from external API: {str(e)}",
            status_code=500
        )