"""
Test script to demonstrate the complete API flow.
Run the FastAPI server first: uvicorn app.main:app --reload --port 8000
"""

import requests
import time
import json
from pathlib import Path

# Configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_IMAGE_URL = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4"  # Mountain landscape


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_response(response, title="Response"):
    """Pretty print API response"""
    print(f"\n{title}:")
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)


def test_root():
    """Test root endpoint to verify API is running"""
    print_section("1. Testing Root Endpoint")
    response = requests.get(f"{BASE_URL}/")
    print_response(response, "API Info")
    return response.status_code == 200


def test_image_caption(image_url):
    """Test image captioning"""
    print_section("2. Testing Image Captioning")
    print(f"Analyzing image: {image_url}")
    
    response = requests.post(
        f"{BASE_URL}/api/analyze/caption",
        json={"image_url": image_url}
    )
    print_response(response, "Caption Result")
    
    if response.status_code == 200:
        caption = response.json()["data"]["caption"]
        print(f"\n✅ Caption: {caption}")
        return True
    return False


def test_object_detection(image_url):
    """Test object detection"""
    print_section("3. Testing Object Detection")
    print(f"Detecting objects in: {image_url}")
    
    response = requests.post(
        f"{BASE_URL}/api/analyze/object-detection",
        json={"image_url": image_url}
    )
    print_response(response, "Object Detection Result")
    
    if response.status_code == 200:
        objects = response.json()["data"]["objects"]
        print(f"\n✅ Objects Found: {objects}")
        return True
    return False


def test_vqa(image_url, question="What colors are visible in this image?"):
    """Test Visual Question Answering"""
    print_section("4. Testing Visual Question Answering (VQA)")
    print(f"Question: {question}")
    print(f"Image: {image_url}")
    
    response = requests.post(
        f"{BASE_URL}/api/analyze/vqa",
        json={
            "image_url": image_url,
            "question": question
        }
    )
    print_response(response, "VQA Result")
    
    if response.status_code == 200:
        answer = response.json()["data"]["answer"]
        print(f"\n✅ Answer: {answer}")
        return True
    return False


def test_text_to_image(prompt="A serene mountain landscape at sunset with pink and orange sky"):
    """Test text-to-image generation"""
    print_section("5. Testing Text-to-Image Generation (ASYNC)")
    print(f"Prompt: {prompt}")
    
    response = requests.post(
        f"{BASE_URL}/api/generate/text-to-image",
        json={"prompt": prompt}
    )
    print_response(response, "Generation Started")
    
    if response.status_code == 200:
        job_id = response.json()["data"]["job_id"]
        print(f"\n✅ Job ID: {job_id}")
        return job_id
    return None


def test_image_variation(image_url, prompt="Make it look like an oil painting with vibrant colors"):
    """Test image variation generation"""
    print_section("6. Testing Image Variation (ASYNC)")
    print(f"Source Image: {image_url}")
    print(f"Variation Prompt: {prompt}")
    
    response = requests.post(
        f"{BASE_URL}/api/generate/variation",
        json={
            "image_url": image_url,
            "prompt": prompt
        }
    )
    print_response(response, "Variation Started")
    
    if response.status_code == 200:
        job_id = response.json()["data"]["job_id"]
        print(f"\n✅ Job ID: {job_id}")
        return job_id
    return None


def poll_job_status(job_id, max_wait=60, interval=3):
    """Poll job status until completion or timeout"""
    print_section(f"7. Polling Job Status: {job_id}")
    print(f"Checking status every {interval} seconds (max {max_wait}s)...")
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        response = requests.get(f"{BASE_URL}/api/jobs/{job_id}")
        
        if response.status_code == 200:
            data = response.json()["data"]
            status = data["status"]
            
            print(f"⏳ Status: {status} (elapsed: {int(time.time() - start_time)}s)")
            
            if status == "completed":
                print_response(response, "✅ Job Completed")
                result_url = data.get("result_image_url")
                if result_url:
                    print(f"\n🖼️  Generated Image URL: {result_url}")
                return True
            elif status == "failed":
                print_response(response, "❌ Job Failed")
                error = data.get("error", "Unknown error")
                print(f"\n❌ Error: {error}")
                return False
            
            # Still processing, wait and retry
            time.sleep(interval)
        else:
            print(f"❌ Failed to check status: {response.status_code}")
            return False
    
    print(f"\n⏰ Timeout reached ({max_wait}s)")
    return False


def run_complete_flow():
    """Run the complete API test flow"""
    print("\n" + "🚀 "*25)
    print("  MULTI-MODAL IMAGE ANALYSIS & GENERATION PLATFORM")
    print("  API Flow Demonstration")
    print("🚀 "*25)
    
    results = {
        "api_running": False,
        "caption": False,
        "object_detection": False,
        "vqa": False,
        "text_to_image": False,
        "image_variation": False
    }
    
    # Test 1: Check if API is running
    try:
        results["api_running"] = test_root()
        if not results["api_running"]:
            print("\n❌ API is not running! Start the server first:")
            print("   cd backend && uvicorn app.main:app --reload --port 8000")
            return results
    except Exception as e:
        print(f"\n❌ Cannot connect to API: {e}")
        print("   Make sure the server is running on http://127.0.0.1:8000")
        return results
    
    # Test 2-4: Analysis Features (Synchronous)
    try:
        results["caption"] = test_image_caption(TEST_IMAGE_URL)
    except Exception as e:
        print(f"\n❌ Caption test failed: {e}")
    
    try:
        results["object_detection"] = test_object_detection(TEST_IMAGE_URL)
    except Exception as e:
        print(f"\n❌ Object detection test failed: {e}")
    
    try:
        results["vqa"] = test_vqa(TEST_IMAGE_URL, "What time of day does this image show?")
    except Exception as e:
        print(f"\n❌ VQA test failed: {e}")
    
    # Test 5-6: Generation Features (Asynchronous)
    print("\n" + "⚠️ "*20)
    print("  WARNING: Image generation may take 30-60 seconds")
    print("  Using FREE tier (HuggingFace Stable Diffusion XL)")
    print("⚠️ "*20)
    
    text_to_image_job_id = None
    variation_job_id = None
    
    try:
        text_to_image_job_id = test_text_to_image()
    except Exception as e:
        print(f"\n❌ Text-to-image test failed: {e}")
    
    try:
        variation_job_id = test_image_variation(TEST_IMAGE_URL)
    except Exception as e:
        print(f"\n❌ Image variation test failed: {e}")
    
    # Poll job statuses
    if text_to_image_job_id:
        try:
            results["text_to_image"] = poll_job_status(text_to_image_job_id, max_wait=90)
        except Exception as e:
            print(f"\n❌ Text-to-image polling failed: {e}")
    
    if variation_job_id:
        try:
            results["image_variation"] = poll_job_status(variation_job_id, max_wait=90)
        except Exception as e:
            print(f"\n❌ Image variation polling failed: {e}")
    
    # Print Summary
    print_section("📊 TEST SUMMARY")
    print("\nResults:")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name:20s}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\n  Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The API is fully functional!")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    return results


if __name__ == "__main__":
    print("\n" + "⚠️ "*20)
    print("  PREREQUISITES:")
    print("  1. FastAPI server must be running:")
    print("     cd backend && uvicorn app.main:app --reload --port 8000")
    print("  2. Environment variables must be set in .env:")
    print("     - GOOGLE_API_KEY (for Gemini)")
    print("     - HF_TOKEN (for Stable Diffusion)")
    print("     - AWS credentials (for S3)")
    print("⚠️ "*20)
    
    input("\n👉 Press Enter to start the test flow... ")
    
    try:
        results = run_complete_flow()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
