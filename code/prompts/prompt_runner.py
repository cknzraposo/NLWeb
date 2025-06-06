# Copyright (c) 2025 Microsoft Corporation.
# Licensed under the MIT License

"""
This file is used to run prompts.

WARNING: This code is under development and may undergo changes in future releases.
Backwards compatibility is not guaranteed at this time.
"""

from prompts.prompts import find_prompt, fill_prompt
from llm.llm import ask_llm
from utils.logging_config_helper import get_configured_logger

logger = get_configured_logger("prompt_runner")

class PromptRunner:

    def get_prompt(self, prompt_name):
        logger.debug(f"Getting prompt: {prompt_name}")
        item_type = self.handler.item_type
        site = self.handler.site
        
        logger.debug(f"Looking for prompt '{prompt_name}' with site='{site}', item_type='{item_type}'")
        prompt_str, ans_struc = find_prompt(site, item_type, prompt_name)

        if (prompt_str is None):
            logger.warning(f"Prompt '{prompt_name}' not found for site='{site}', item_type='{item_type}'")
            return None, None
        
        logger.debug(f"Found prompt '{prompt_name}', length: {len(prompt_str)} chars")
        return prompt_str, ans_struc

    def __init__(self, handler):
        self.handler = handler
        logger.debug(f"PromptRunner initialized with handler for site: {handler.site}")

    async def run_prompt(self, prompt_name, level="low", verbose=False, timeout=8):
        logger.info(f"Running prompt: {prompt_name} with level={level}, timeout={timeout}s")
        
        try:
            prompt_str, ans_struc = self.get_prompt(prompt_name)
            if (prompt_str is None):
                if (verbose):
                    print(f"Prompt {prompt_name} not found")
                logger.debug(f"Cannot run prompt '{prompt_name}' - prompt not found")
                return None
        
            logger.debug(f"Filling prompt template with handler data")
            prompt = fill_prompt(prompt_str, self.handler)
            if (verbose):
                print(f"Prompt: {prompt}")
            logger.debug(f"Filled prompt length: {len(prompt)} chars")
            
            logger.info(f"Calling LLM with level={level}")
            response = await ask_llm(prompt, ans_struc, level=level, timeout=timeout, query_params=self.handler.query_params)
            
            if response is None:
                logger.warning(f"LLM returned None for prompt '{prompt_name}'")
            else:
                logger.info(f"LLM response received for prompt '{prompt_name}'")
                logger.debug(f"Response type: {type(response)}, size: {len(str(response))} chars")
            
            if (verbose):
                print(f"Response: {response}")
            
            return response
            
        except Exception as e:
            from config.config import CONFIG
            error_msg = f"Error in run_prompt for '{prompt_name}': {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            logger.debug("Full traceback:", exc_info=True)
            
            if CONFIG.should_raise_exceptions():
                # In testing/development mode, re-raise with enhanced error message
                raise Exception(f"LLM call failed for prompt '{prompt_name}': {type(e).__name__}: {str(e)}") from e
            else:
                # In production mode, log and return None
                print(f"ERROR in run_prompt: {type(e).__name__}: {str(e)}")
                return None