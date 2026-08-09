class ConversationMemory:
    """
    Stores dataset and conversation context for the Statistics AI Agent.
    """

    def __init__(self, max_history=10):
        self.last_question = None
        self.last_result = None
        self.last_dataframe = None
        self.filename = None

        # Store recent conversation history
        self.history = []

        # Maximum number of conversations to remember
        self.max_history = max_history

    # --------------------------------------------------
    # UPDATE MEMORY
    # --------------------------------------------------

    def update(
        self,
        question=None,
        result=None,
        dataframe=None,
        filename=None
    ):
        """
        Update the agent memory.
        """

        if question is not None:
            self.last_question = question

        if result is not None:
            self.last_result = result

        if dataframe is not None:
            self.last_dataframe = dataframe

        if filename is not None:
            self.filename = filename

        # Store conversation pair
        if question is not None or result is not None:

            conversation = {
                "question": question,
                "result": result
            }

            self.history.append(conversation)

            # Keep only the latest conversations
            if len(self.history) > self.max_history:
                self.history.pop(0)

    # --------------------------------------------------
    # GET LAST QUESTION
    # --------------------------------------------------

    def get_last_question(self):
        return self.last_question

    # --------------------------------------------------
    # GET LAST RESULT
    # --------------------------------------------------

    def get_last_result(self):
        return self.last_result

    # --------------------------------------------------
    # GET DATAFRAME
    # --------------------------------------------------

    def get_dataframe(self):
        return self.last_dataframe

    # --------------------------------------------------
    # GET FILENAME
    # --------------------------------------------------

    def get_filename(self):
        return self.filename

    # --------------------------------------------------
    # GET CONVERSATION HISTORY
    # --------------------------------------------------

    def get_history(self):
        return self.history

    # --------------------------------------------------
    # GET RECENT HISTORY
    # --------------------------------------------------

    def get_recent_history(self, n=5):
        """
        Return the most recent n conversations.
        """

        return self.history[-n:]

    # --------------------------------------------------
    # CLEAR MEMORY
    # --------------------------------------------------

    def clear(self):
        """
        Clear all stored memory.
        """

        self.last_question = None
        self.last_result = None
        self.last_dataframe = None
        self.filename = None
        self.history = []


# Global memory instance
memory = ConversationMemory()