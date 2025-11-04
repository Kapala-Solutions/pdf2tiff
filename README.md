# PDF to TIFF Converter - Azure Function

A serverless Azure Function that converts PDF files to TIFF format. Supports both single-page and multi-page PDFs with high-quality 300 DPI output.

## Features

- ✅ Converts PDF to TIFF (single or multi-page)
- ✅ High-quality 300 DPI rendering
- ✅ TIFF deflate compression for smaller file sizes
- ✅ No external dependencies (pure Python)
- ✅ Serverless architecture using Azure Functions
- ✅ HTTP trigger with multipart/form-data support

## Prerequisites

- Python 3.9 or higher
- Azure Functions Core Tools (for local development)
- Azure subscription (for deployment)
- Azure CLI (for deployment)

## Local Development Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Azure Functions Core Tools

**Windows (with npm):**
```bash
npm install -g azure-functions-core-tools@4 --unsafe-perm true
```

**Windows (with MSI):**
Download from: https://aka.ms/V4FunctionsCoreTools

**macOS:**
```bash
brew tap azure/functions
brew install azure-functions-core-tools@4
```

**Linux (Ubuntu/Debian):**
```bash
wget -q https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install azure-functions-core-tools-4
```

### 3. Run Locally

```bash
func start
```

The function will be available at: `http://localhost:7071/api/convertpdf2tiff`

## Testing the Function

### Method 1: Using the Test Script

```bash
python test_local.py your-file.pdf
```

This will create `output.tiff` in the project root.

### Method 2: Using Postman

1. Create a new POST request
2. URL: `http://localhost:7071/api/convertpdf2tiff`
3. Go to **Body** tab
4. Select **form-data**
5. Add key: `file` (change type to "File")
6. Select your PDF file
7. Click **Send**
8. Click **Save Response** → **Save to a file** → Save as `converted.tiff`

### Method 3: Using cURL

```bash
curl -X POST "http://localhost:7071/api/convertpdf2tiff" \
  -F "file=@yourfile.pdf" \
  --output converted.tiff
```

### Method 4: Using PowerShell

```powershell
$uri = "http://localhost:7071/api/convertpdf2tiff"
$filePath = "C:\path\to\your\file.pdf"
$fileContent = [System.IO.File]::ReadAllBytes($filePath)
$boundary = [System.Guid]::NewGuid().ToString()
$contentType = "multipart/form-data; boundary=$boundary"

$body = @"
--$boundary
Content-Disposition: form-data; name="file"; filename="test.pdf"
Content-Type: application/pdf

$([System.Text.Encoding]::GetEncoding('iso-8859-1').GetString($fileContent))
--$boundary--
"@

Invoke-RestMethod -Uri $uri -Method Post -ContentType $contentType -Body $body -OutFile "converted.tiff"
```

## Deploy to Azure

### Step 1: Install Azure CLI

**Windows:**
Download from: https://aka.ms/installazurecliwindows

**macOS:**
```bash
brew update && brew install azure-cli
```

**Linux:**
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### Step 2: Login to Azure

```bash
az login
```

This will open a browser window for authentication.

### Step 3: Create a Resource Group

```bash
az group create --name pdf2tiff-rg --location eastus
```

Replace `eastus` with your preferred region (e.g., `westus2`, `northeurope`, `southeastasia`).

### Step 4: Create a Storage Account

```bash
az storage account create \
  --name pdf2tiffstorage \
  --resource-group pdf2tiff-rg \
  --location eastus \
  --sku Standard_LRS
```

**Note:** Storage account names must be unique across Azure, so use a unique name like `pdf2tiff<yourname>storage`.

### Step 5: Create a Function App

```bash
az functionapp create \
  --resource-group pdf2tiff-rg \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name pdf2tiff-func \
  --storage-account pdf2tiffstorage \
  --os-type Linux
```

**Note:** Function app names must be globally unique. Use something like `pdf2tiff-func-<yourname>`.

### Step 6: Deploy the Function

From your project directory:

```bash
func azure functionapp publish pdf2tiff-func
```

Replace `pdf2tiff-func` with your actual function app name.

### Step 7: Get the Function URL and Key

After deployment, get your function URL:

```bash
az functionapp function show \
  --name pdf2tiff-func \
  --resource-group pdf2tiff-rg \
  --function-name convertpdf2tiff \
  --query invokeUrlTemplate -o tsv
```

Get the function key:

```bash
az functionapp keys list \
  --name pdf2tiff-func \
  --resource-group pdf2tiff-rg \
  --query functionKeys.default -o tsv
```

### Step 8: Test the Deployed Function

```bash
curl -X POST "https://pdf2tiff-func.azurewebsites.net/api/convertpdf2tiff?code=YOUR_FUNCTION_KEY" \
  -F "file=@yourfile.pdf" \
  --output converted.tiff
```

## Alternative: Deploy Using VS Code

### 1. Install VS Code Extensions

- Azure Functions Extension
- Python Extension

### 2. Deploy Steps

1. Open the project in VS Code
2. Click on the **Azure** icon in the sidebar
3. Sign in to Azure
4. Click **Deploy to Function App** (↑ icon)
5. Follow the prompts:
   - Select subscription
   - Create new Function App or select existing
   - Choose a unique name
   - Select Python 3.11
   - Select a region
6. Wait for deployment to complete

### 3. Test in VS Code

1. In the Azure Functions extension, expand your function app
2. Right-click on the function → **Copy Function URL**
3. Use Postman or cURL to test with the URL

## Configuration Options

### Adjust Image Quality (DPI)

Edit [function_app.py](function_app.py:34):

```python
# Change 300 to your desired DPI (e.g., 150, 200, 600)
pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
```

Higher DPI = better quality but larger files.

### Change Compression

Edit [function_app.py](function_app.py:52):

```python
# Options: 'tiff_deflate', 'tiff_lzw', 'tiff_jpeg', None
compression='tiff_deflate'
```

## Monitoring and Logs

### View logs locally:
Logs appear in the terminal when running `func start`

### View logs in Azure:

```bash
az functionapp logs tail \
  --name pdf2tiff-func \
  --resource-group pdf2tiff-rg
```

Or use **Application Insights** in the Azure Portal for detailed monitoring.

## Troubleshooting

### "No attribute 'files'" error
Make sure you're sending the request as `multipart/form-data` with a file field named `file`.

### Function timeout
For very large PDFs, increase the function timeout in [host.json](host.json):

```json
{
  "version": "2.0",
  "functionTimeout": "00:10:00",
  "logging": {
    ...
  }
}
```

### Memory issues with large PDFs
Consider upgrading to a Premium plan for more memory:

```bash
az functionapp plan create \
  --resource-group pdf2tiff-rg \
  --name pdf2tiff-premium-plan \
  --location eastus \
  --sku EP1 \
  --is-linux

az functionapp update \
  --name pdf2tiff-func \
  --resource-group pdf2tiff-rg \
  --plan pdf2tiff-premium-plan
```

## Cost Estimation

**Consumption Plan (Pay-as-you-go):**
- First 1 million executions: Free
- After: $0.20 per million executions
- Memory usage: ~$0.000016/GB-second

Typical conversion: 2-3 seconds for a 10-page PDF ≈ $0.0001 per conversion

## Clean Up Resources

To delete all Azure resources:

```bash
az group delete --name pdf2tiff-rg --yes --no-wait
```

## Project Structure

```
pdf2tiff/
├── function_app.py       # Main function code
├── requirements.txt      # Python dependencies
├── host.json            # Function app configuration
├── .funcignore          # Files to exclude from deployment
├── test_local.py        # Local testing script
└── README.md            # This file
```

## API Reference

### Endpoint

`POST /api/convertpdf2tiff`

### Request

- **Content-Type:** `multipart/form-data`
- **Body:** Form field named `file` containing the PDF file

### Response

- **Success (200):**
  - Content-Type: `image/tiff`
  - Body: TIFF file binary data
  - Header: `Content-Disposition: attachment; filename="converted.tiff"`

- **Error (400):**
  - Missing file parameter

- **Error (500):**
  - Conversion error with details

## License

MIT License

## Support

For issues or questions, please open an issue on the project repository.
