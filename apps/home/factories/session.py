""" Boto3 factory definition. """

import os

from boto3.session import Session  # type: ignore

from apps.home.factories.logger import LoggerFactory

logger = LoggerFactory.get_logger(__name__)


class Boto3SessionFactory:
    @staticmethod
    def get_or_create(use_local_session: bool = True) -> Session:
        """Get an boto3 Session based on local configuration or environment variable.
        Environment vars utilized: {AWS_ACCESS_KEY_ID}, {AWS_SECRET_ACCESS_KEY} and {AWS_DEFAULT_REGION} by default us-east-1
        Args:
            use_local_session (bool, optional): The local session will be used avoiding search for ENV vars. Defaults to True.
        Raises:
            ConfigVarNotFoundError: S3 session variables not encountered, use_local_session=true or set env vars
        Returns:
            Session: boto3 Session to use clients such as s3 or sagemaker
        """
        if use_local_session:
            session = Session(
                region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
            )
            logger.info("Using local s3 session configuration.")
        elif (
            "AWS_ACCESS_KEY_ID" in os.environ and "AWS_SECRET_ACCESS_KEY" in os.environ
        ):
            aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
            aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]
            aws_default_region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
            aws_session_token = os.environ.get("AWS_SESSION_TOKEN", None)
            if not aws_session_token:
                session = Session(
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    region_name=aws_default_region,
                )
            else: 
                session = Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token,
                region_name=aws_default_region,
            )
            logger.info("Using {ENV} s3 session configuration.")
        else:
            message = "S3 session variables not encountered, use_local_session=true or set env vars: {AWS_ACCESS_KEY_ID} and {AWS_SECRET_ACCESS_KEY}!!"
            logger.error(message)
            raise Exception(message)
        return session