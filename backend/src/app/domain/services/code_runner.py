from abc import ABC, abstractmethod

from src.app.domain.models.dto.execution.runner_result import RunnerExecutionResultDTO


class CodeRunner(ABC):
    @abstractmethod
    async def execute(self, source_code: str) -> RunnerExecutionResultDTO:
        """
        Execute source code in remote runner.

        The interface decouples execution orchestration from a concrete runtime
        provider so tests can stub runner behavior directly.

        :param source_code: source code to execute

        :return: runner execution result
        """
        raise NotImplementedError
