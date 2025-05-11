"""
    Communication with GCS
    - attributes
        - client
        - buckets
    - methods
        - exists
            - folders
            - files
        - Upload
        - Delete
        - Download
"""

from google.cloud import storage

class GCSGateway:
    def __init__(self):
        self.client = storage.Client()
        self.bucket = None
        
    def connect_bucket(self, bucket_name: str):
        """Connect the bucket"""
        self.bucket = self.client.bucket(bucket_name)
        
    def get_blob(self, blob_name: str):
        return self.bucket.blob(blob_name)
    
    def list_blobs_with_prefix(self, prefix: str, delimiter: str|None = None) -> list[str]:
        """Lists all the blobs in the bucket that begin with the prefix.

        This can be used to list all blobs in a "folder", e.g. "public/".

        The delimiter argument can be used to restrict the results to only the
        "files" in the given "folder". Without the delimiter, the entire tree under
        the prefix is returned. For example, given these blobs:

            a/1.txt
            a/b/2.txt

        If you specify prefix ='a/', without a delimiter, you'll get back:

            a/1.txt
            a/b/2.txt

        However, if you specify prefix='a/' and delimiter='/', you'll get back
        only the file directly under 'a/':

            a/1.txt

        As part of the response, you'll also get back a blobs.prefixes entity
        that lists the "subfolders" under `a/`:

            a/b/
        """

        storage_client = storage.Client()

        # Note: Client.list_blobs requires at least package version 1.17.0.
        blobs = self.client.list_blobs(bucket_name, prefix=prefix, delimiter=delimiter)
        
        # Get all blob name in a specific prefix
        blob_list = [blob.name for blob in blobs] + [prefix for prefix in blobs.prefixes]
        return blob_list
        
    
    def check_exists(self, path: str) -> bool:
        """Check the path exists in GCS

        Args:
            path (str): a path that is checked in all GCS.
                        if you want to specify folders, you should write "/" in the end. 
                        e.g. delay directory -> "delay/"

        Returns:
            bool: Return the flag whether path exists.
        """
        blob_list = self.list_blobs_with_prefix(dir, "/") 
        return path in blob_list
        
    def upload_blob(self, source_file_name: str, destination_blob_name: str):
        """Upload the blob"""
        
        # Upload when the destination blob doensn't exist
        if not self.check_exists(destination_blob_name):
            blob = self.bucket.blob(destination_blob_name)
            # Optional: set a generation-match precondition to avoid potential race conditions
            # and data corruptions. The request to upload is aborted if the object's
            # generation number does not match your precondition. For a destination
            # object that does not yet exist, set the if_generation_match precondition to 0.
            # If the destination object already exists in your bucket, set instead a
            # generation-match precondition using its generation number.
            generation_match_precondition = 0 

            blob.upload_from_filename(source_file_name, if_generation_match=generation_match_precondition)

    def download_blob(self, source_blob_name: str, destination_file_name: str):
        """Downloads a blob from the bucket."""
        blob = self.bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)

    def delete_blob(self, blob_name: str):
        """Deletes a blob from the bucket."""
        blob = self.bucket.blob(blob_name)
        generation_match_precondition = None

        # Optional: set a generation-match precondition to avoid potential race conditions
        # and data corruptions. The request to delete is aborted if the object's
        # generation number does not match your precondition.
        blob.reload()  # Fetch blob metadata to use in generation_match_precondition.
        generation_match_precondition = blob.generation

        blob.delete(if_generation_match=generation_match_precondition)
        
