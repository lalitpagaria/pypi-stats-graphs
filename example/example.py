from pypi_stats_utils.data_fetcher import PyPiDataFetcher

data_fetcher = PyPiDataFetcher(
    package='obsei'
)

print(data_fetcher.get_stats())
