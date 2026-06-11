from daq_core.storage import SQLiteSampleRepository


repo = SQLiteSampleRepository("data/daq.db")


def get_repository() -> SQLiteSampleRepository:
    return repo