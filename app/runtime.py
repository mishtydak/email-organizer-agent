from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AuditEntry:
    action: str
    inputs: dict
    outputs: object
    timestamp: str





@dataclass
class Runtime:
    audit_log: list[AuditEntry] = field(default_factory=list)
    checkpoint: dict | None = None
    action_count: int = 0
    max_actions: int = 5

    def execute(self, action_name, action, **inputs):
     """
      Execute an action within the runtime budget.
      """

     if self.action_count >= self.max_actions:
        raise RuntimeError("Runtime action budget exceeded.")

     output = action(**inputs)

     self.action_count += 1

     self.audit_log.append(
        AuditEntry(
            action=action_name,
            inputs=inputs,
            outputs=output,
            timestamp=datetime.now().isoformat()
        )
    )

     self.checkpoint = {
        "last_action": action_name,
        "inputs": inputs,
        "output": output
    }

     return output
      
    def get_checkpoint(self):
        """
        Return the latest successful checkpoint.
        """
        return self.checkpoint

    def resume(self):
        """
        Return information about where the run can resume.
        """
        if self.checkpoint is None:
            return "No checkpoint available."

        return (
            f"Resume from action: "
            f"{self.checkpoint['last_action']}"
        )


    
    def require_approval(self, action_name: str) -> bool:
      """
      Human approval gate for consequential actions.
      """

      print(f"\nApproval required for: {action_name}")

      response = input(
        "Approve this action? (yes/no): "
     )

      return response.lower() == "yes"
  
    

