import boto3
import botocore
from pathlib import Path
import time
from deep_translator import GoogleTranslator
from fpdf import FPDF
import json

#==========================================================================
# Initialize clients
#==========================================================================
s3 = boto3.client('s3')
bucket = "2025dokwood"
textract = boto3.client("textract")
#==========================================================================
# Step 1: Call Textract (example for local file)
#==========================================================================
file_path = Path("data/pdf")
pdf_file = file_path / "VKF_13-15.pdf"
# Upload to S3
def file_exists_in_s3(bucket:str, key: str):
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        raise

if not file_exists_in_s3(bucket, pdf_file.name):
    s3.upload_file(str(pdf_file), bucket, pdf_file.name)
    print(f"✅ Uploaded {pdf_file} to s3://{bucket}/{pdf_file}")
else:
    print(f"⏭️ Skipped upload: {pdf_file} already exists in s3://{bucket}/")
#==========================================================================
# Step 2: Extract text lines
#==========================================================================
textract = boto3.client('textract')
response = textract.start_document_text_detection(
    DocumentLocation={
        'S3Object': {
            'Bucket': bucket,
            'Name': pdf_file.name
        }
    },
    NotificationChannel={
        'RoleArn': 'arn:aws:iam::613168617177:role/texttract_s3',
        'SNSTopicArn': 'arn:aws:sns:eu-central-1:613168617177:textract-completion-topic'
    },
    OutputConfig={
        'S3Bucket': bucket
    }
)
job_id = response['JobId']
print("Started Textract job:", job_id)
#==========================================================================
# Step 3: Pole the extraction job status
#==========================================================================
def is_job_complete(job_id):
    while True:
        response = textract.get_document_text_detection(JobId=job_id)
        status = response['JobStatus']
        print("Job status:", status)
        if status in ['SUCCEEDED', 'FAILED']:
            return status == 'SUCCEEDED'
        time.sleep(10)
is_job_complete(job_id)
#==========================================================================
# Step 4: Get translated text
#==========================================================================
def get_job_results(s3, job_id, bucket):
    key = f"textract_output/{job_id}/1"
    # Try to retrieve the metadata for the file '1'
    try:
        s3.head_object(Bucket=bucket, Key=key)  # checks if file exists without downloading
        return key
    except s3.exceptions.ClientError as e:
        raise FileNotFoundError(f"No Textract output found for job {job_id} in bucket {bucket}.") from e
output_key  = get_job_results(s3, job_id, bucket)
#==========================================================================
# Step 5: Retrieve Rresult
#==========================================================================
def get_job_results(job_id):
    # Download and parse it
    s3.download_file(bucket, output_key, "result.json")
    with open("result.json", "r", encoding="utf-8") as f:
        result_json = json.load(f)

    # Then extract the text blocks etc.
    lines = [block['Text'] for block in result_json['Blocks'] if block['BlockType'] == 'LINE']
    return lines
lines = get_job_results(job_id)
#==========================================================================
# Step 6: Translate
#==========================================================================
# === Step 1: Load Textract JSON ===
with open("result.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# === Step 2: Organize lines by page ===
page_texts = {}
for block in data["Blocks"]:
    if block["BlockType"] == "LINE":
        page_number = block["Page"]
        text = block.get("Text", "").strip()
        if text:
            page_texts.setdefault(page_number, []).append(text)

# === Step 3: Translate text blocks page by page ===
translated_pages = {}
for page_num, lines in page_texts.items():
    german_text = "\n".join(lines)
    chunks = [german_text[i:i+4500] for i in range(0, len(german_text), 4500)]
    translated_chunks = [GoogleTranslator(source="de", target="en").translate(chunk) for chunk in chunks]
    translated_text = "\n".join(translated_chunks)
    translated_pages[page_num] = translated_text

# === Step 4: Write to a PDF ===
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.set_font("Arial", size=12)

for page_num in sorted(translated_pages.keys()):
    pdf.add_page()
    pdf.multi_cell(0, 10, translated_pages[page_num])

pdf.output("translated_output.pdf")
print("✅ Translated PDF saved as 'translated_output.pdf'")