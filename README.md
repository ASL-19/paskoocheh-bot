# PaskoochehBot

A Telegram Bot for serving downloads in response to user messages through the Telegram API.

## Configuration

### Python

* Create src/conf_access.json with the following structure:

        {
            "LIMITED_ACCESS": {
                "API_KEY_ID": "<s3 temp key id>",
                "SECRET_KEY": "<s3 temp secret key>"
            }
        }

The api credentials should have read only access to the bucket serving the paskoocheh files.

### S3 Bucket with Downloads

* point settings.py at configuration file in JSON in bucket with `S3_BUCKET_NAME` and `S3_CONF_BUCKET_KEY`
* configuration file should have the following structure
  * For each download to be served:

        [{
            "name": "<downloadName>",
            "os": "<downloadOSName>",
            "filename": "<downloadFileName>",
            "email_addr": "<autoresponderEmail>",
            "body": [[
                "plain", "<emailPlainBody>"
            ], [
                "html", "<emailHTMLBody>"
            ]],
            "attachments": [[
                "<downloadBucket>",
                "<downloadBucketKey>",
                "<emailFilename>"
            ]]
        }]

