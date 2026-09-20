import time
from config import WARNING_TIME


class EmployeeTracker:

    def __init__(self):

        self.data = {}

    def update(self, name, mask_status):

        current_time = time.time()

        # New Employee
        if name not in self.data:

            self.data[name] = {

                "start_time": current_time,
                "warning_count": 0,
                "mail_sent": False

            }

        employee = self.data[name]

        # -------------------------
        # Employee Wearing Mask
        # -------------------------

        if mask_status == "mask":

            employee["start_time"] = current_time
            employee["mail_sent"] = False

            return False

        # -------------------------
        # Employee Without Mask
        # -------------------------

        elapsed = current_time - employee["start_time"]

        if elapsed >= WARNING_TIME and employee["mail_sent"] is False:

            employee["warning_count"] += 1
            employee["mail_sent"] = True

            print(
                f"{name} Warning : {employee['warning_count']}"
            )

            return True

        return False

    # -------------------------
    # Get Warning Count
    # -------------------------

    def get_warning_count(self, name):

        if name not in self.data:

            return 0

        return self.data[name]["warning_count"]

    # -------------------------
    # Reset Employee
    # -------------------------

    def reset(self, name):

        if name in self.data:

            self.data[name]["start_time"] = time.time()
            self.data[name]["mail_sent"] = False

