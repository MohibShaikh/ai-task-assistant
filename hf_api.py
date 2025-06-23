import requests
import os
from typing import List, Union
import numpy as np

class HuggingFaceAPI:
    """Wrapper for Hugging Face Inference API to replace local sentence transformers."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-mpnet-base-v2", api_token: str = None):
        self.model_name = model_name
        self.api_token = api_token or os.getenv('HF_TOKEN')
        self.base_url = f"https://api-inference.huggingface.co/models/{model_name}"
        print(f"[HF_API] Using model: {self.model_name}")
        if not self.api_token:
            print("⚠️  Warning: No HF_TOKEN found. Please set HF_TOKEN environment variable.")
    
    def encode(self, texts: Union[str, List[str]], **kwargs) -> np.ndarray:
        """
        Encode text(s) to embeddings using Hugging Face API.
        
        Args:
            texts: Single text string or list of text strings
            **kwargs: Additional arguments (ignored for API)
            
        Returns:
            numpy array of embeddings
        """
        if not self.api_token:
            # Fallback to dummy embeddings if no token
            if isinstance(texts, str):
                return np.random.rand(1, 768)
            else:
                return np.random.rand(len(texts), 768)
        
        # Convert single text to list
        if isinstance(texts, str):
            texts = [texts]
        
        try:
            response = requests.post(
                self.base_url,
                headers={"Authorization": f"Bearer {self.api_token}"},
                json={"inputs": texts},
                timeout=30
            )
            
            if response.status_code == 200:
                embeddings = response.json()
                # Convert to numpy array
                if isinstance(embeddings, list):
                    return np.array(embeddings)
                else:
                    return np.array([embeddings])
            else:
                # Special warning for sentence-similarity pipeline
                if response.status_code == 400 and 'SentenceSimilarityPipeline' in response.text:
                    print(f"❌ API Error: {response.status_code} - {response.text}")
                    print("\n[HF_API] It looks like you are using a model with the 'sentence-similarity' pipeline.\n"
                          "Please use a model with the 'feature-extraction' pipeline for embeddings, such as:\n"
                          "- sentence-transformers/all-mpnet-base-v2\n"
                          "- sentence-transformers/all-MiniLM-L6-v2\n"
                          "- sentence-transformers/paraphrase-multilingual-mpnet-base-v2\n"
                          "Or update your payload to use the correct format for sentence-similarity.")
                else:
                    print(f"❌ API Error: {response.status_code} - {response.text}")
                # Fallback to dummy embeddings
                return np.random.rand(len(texts), 768)
                
        except Exception as e:
            print(f"❌ API Request failed: {e}")
            # Fallback to dummy embeddings
            return np.random.rand(len(texts), 768)
    
    def __call__(self, texts: Union[str, List[str]], **kwargs) -> np.ndarray:
        """Alias for encode method."""
        return self.encode(texts, **kwargs)

# Global instance for easy access
GLOBAL_HF_MODEL = HuggingFaceAPI()

def get_embeddings(texts: Union[str, List[str]]) -> np.ndarray:
    """Helper function to get embeddings from Hugging Face API."""
    return GLOBAL_HF_MODEL.encode(texts) 