from pypi_stats_graphs.data_fetcher import PyPiDataFetcher

data_fetcher = PyPiDataFetcher(
    package='obsei'
)

print(data_fetcher.get_query_results())
