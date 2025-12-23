# S3 CORS Configuration for Image Downloads

## Why CORS Configuration is Needed

The frontend download feature uses `fetch()` to download images from S3. For this to work properly across origins, your S3 bucket needs CORS (Cross-Origin Resource Sharing) configuration.

## Current Setup Status

✅ **Presigned URLs work** - Images can be accessed via presigned URLs (7-day expiry)
✅ **Next.js Image component works** - Images display correctly in the UI
⚠️ **Download feature needs CORS** - For programmatic downloads via fetch()

## How the Download Feature Works

### Without CORS Configuration:
- Browser blocks fetch() requests due to CORS policy
- **Fallback:** Download button opens image in new tab
- User can then right-click → Save As

### With CORS Configuration:
- fetch() downloads image directly
- Automatic save to downloads folder
- Better user experience

## Setting Up S3 CORS

### Option 1: AWS Console (Recommended for Beginners)

1. **Go to AWS S3 Console**
   - Navigate to https://s3.console.aws.amazon.com/
   - Select your bucket

2. **Open Permissions Tab**
   - Click on "Permissions"
   - Scroll down to "Cross-origin resource sharing (CORS)"

3. **Add CORS Configuration**
   - Click "Edit"
   - Paste the configuration below
   - Click "Save changes"

### CORS Configuration JSON

```json
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "GET",
            "HEAD"
        ],
        "AllowedOrigins": [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://your-production-domain.com"
        ],
        "ExposeHeaders": [
            "Content-Length",
            "Content-Type",
            "ETag"
        ],
        "MaxAgeSeconds": 3600
    }
]
```

### Configuration Explanation

| Field | Purpose |
|-------|---------|
| `AllowedHeaders` | Allows all request headers (`*`) |
| `AllowedMethods` | Permits GET and HEAD requests for downloading |
| `AllowedOrigins` | Frontend domains allowed to access S3 |
| `ExposeHeaders` | Headers the browser can access |
| `MaxAgeSeconds` | How long browsers cache CORS preflight (1 hour) |

### Option 2: AWS CLI

```bash
# Create cors.json file with the configuration above, then:
aws s3api put-bucket-cors \
    --bucket YOUR_BUCKET_NAME \
    --cors-configuration file://cors.json
```

### Option 3: Using Boto3 (Python)

```python
import boto3
import json

s3_client = boto3.client('s3')

cors_configuration = {
    'CORSRules': [{
        'AllowedHeaders': ['*'],
        'AllowedMethods': ['GET', 'HEAD'],
        'AllowedOrigins': [
            'http://localhost:3000',
            'http://127.0.0.1:3000',
            'https://your-production-domain.com'
        ],
        'ExposeHeaders': ['Content-Length', 'Content-Type', 'ETag'],
        'MaxAgeSeconds': 3600
    }]
}

s3_client.put_bucket_cors(
    Bucket='YOUR_BUCKET_NAME',
    CORSConfiguration=cors_configuration
)
```

## Testing CORS Configuration

### 1. Verify CORS is Applied

```bash
aws s3api get-bucket-cors --bucket YOUR_BUCKET_NAME
```

### 2. Test in Browser

1. Open browser DevTools (F12)
2. Go to Network tab
3. Generate an image in the app
4. Click Download button
5. Check for CORS errors in console

**Without CORS:**
```
Access to fetch at 'https://bucket.s3.amazonaws.com/...' from origin 'http://localhost:3000' 
has been blocked by CORS policy
```

**With CORS:**
```
✅ No errors - Image downloads successfully
```

## Production Deployment

### Update AllowedOrigins

When deploying to production, update the CORS configuration to include your production domain:

```json
"AllowedOrigins": [
    "https://your-app.vercel.app",
    "https://your-custom-domain.com"
]
```

### Security Best Practices

1. **Don't use wildcard (`*`) in production**
   - Specify exact domains
   - Example: `"AllowedOrigins": ["https://myapp.com"]`

2. **Limit Methods**
   - Only allow necessary methods (GET, HEAD)
   - Don't allow PUT, POST, DELETE for public access

3. **Use Presigned URLs**
   - Already implemented ✅
   - Presigned URLs provide temporary access
   - Expire after 7 days

## Alternative: Proxy Through Backend

If you can't configure S3 CORS, you can proxy downloads through your backend:

### Backend Route (FastAPI)

```python
@app.get("/download/{image_id}")
async def download_image(image_id: str):
    # Fetch image from S3
    s3_client = get_s3_client()
    obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=f"generated/{image_id}.png")
    
    return StreamingResponse(
        obj['Body'],
        media_type="image/png",
        headers={
            "Content-Disposition": f"attachment; filename=image-{image_id}.png"
        }
    )
```

### Frontend Update

```typescript
const handleDownload = async () => {
  // Extract image ID from S3 URL
  const imageId = src.split('/').pop()?.split('.')[0];
  window.location.href = `${API_BASE_URL}/download/${imageId}`;
};
```

## Current Implementation

The download feature **works even without CORS** by using fallback methods:

1. **Primary:** Fetch + Blob (requires CORS)
2. **Fallback:** Direct link download (works with presigned URLs)
3. **Last resort:** Opens image in new tab

So your app is **functional right now**, but CORS configuration will provide a better UX.

## Recommended Action

**For Development:**
- ✅ Current implementation works (uses fallback)
- Optional: Add CORS for smoother downloads

**For Production:**
- ⚠️ **Required:** Configure CORS with your production domain
- Improves user experience
- Enables proper programmatic downloads

## Troubleshooting

### Issue: CORS errors in console
**Solution:** Apply CORS configuration as shown above

### Issue: Download opens in new tab instead of saving
**Solution:** 
- This is the fallback behavior (working as intended)
- To fix: Configure CORS

### Issue: Images don't display at all
**Solution:** 
- Check S3 bucket permissions
- Verify presigned URLs are being generated
- Check Next.js image domain configuration

## Questions?

If you encounter issues:
1. Check AWS CloudWatch logs
2. Verify bucket permissions
3. Test presigned URLs directly in browser
4. Check browser console for specific errors

---

**Status:** Download feature is **functional** with fallback methods. CORS configuration is **optional but recommended** for production.
