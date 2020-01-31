from ScoutSuite.core.console import print_exception
from ScoutSuite.providers.aws.facade.utils import AWSFacadeUtils
from ScoutSuite.providers.aws.facade.basefacade import AWSBaseFacade
from ScoutSuite.providers.utils import run_concurrently

class DynamoDbFacade(AWSBaseFacade):

    async def get_tables(self, region):
        try:
            return await AWSFacadeUtils.get_all_pages('dynamodb', region, self.session, 'list_tables', 'TableNames')
        except Exception as e:
            print_exception('Failed to get DynamoDB tables: {}'.format(e))
            return []

    async def get_global_tables(self, region: str):
        try:
            dynamodb_client = AWSFacadeUtils.get_client('dynamodb', self.session, region)
            return await run_concurrently(lambda: dynamodb_client.list_global_tables(RegionName=region))
        except Exception as e:
            print_exception('Failed to get DynamoDB global tables: {}'.format(e))
            return []

