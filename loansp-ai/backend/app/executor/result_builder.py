class ResultBuilder:
    def build(self, execution_results):

        outputs = []

        for result in execution_results:
            if not result.success:
                outputs.append(f"Lỗi: {result.error}")

                continue

            if result.task == "calculate_dti":
                dti = result.data["dti"]

                outputs.append(f"DTI hiện tại là {dti * 100:.2f}%")

        return "\n".join(outputs)
