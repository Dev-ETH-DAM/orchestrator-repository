import json

task_json_key = "TASK_SETUP"

class RequestedWorkTask:
    params = None
    result_params = None
    result_values = None
    
    def set_params(self, configuration_json:str):
        """Sets the parameters for the task, the default
        is to just save the json, but it is recommended
        to have your own parameter logic.

        Args:
            configuration_json (str): a json grabbed from 
            the task where the orchestrator can 
            add extra parameters. The orchestrator needs to
            provide only the task part.
        """
        self.params = json.loads(configuration_json)

    def start_working(self):
        """Specific logic for each task worker.

        At the end of the task result_params and
        result_values need to be set in order return the 
        results and later validate them.
        """
        self.result_params = {}
        self.result_values = {}

    def get_results(self) -> tuple[dict, dict]:
        """Returns a pair of parameters and results
        resulted from the work of the agent.

        The parameters are required in order to validate
        the legitimity of the results.

        Returns:
            tuple[dict, dict]: result_parameters, result_values
        """
        return (self.result_params, self.result_values)