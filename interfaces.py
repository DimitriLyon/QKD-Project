import math


class Simulator:
    def __init__(self, endpoints, length, len_err, fiber_speed):
        self.endpoints = endpoints
        self.length = length
        self.len_err = len_err
        self.fiber_speed = fiber_speed
        self.error_sources = {"fiber_length": 1 - math.exp(-len_err * length)}

    def add_err_source(self, name, err_rate):
        self.error_sources[name] = err_rate

    def get_total_error(self):
        total_success = 1.0
        for err in self.error_sources.values():
            total_success *= 1 - err
        return 1 - total_success

    def change_endpoints(self, new_endpoints):
        self.endpoints = new_endpoints

    def run(self, key_len):
        total_error = self.get_total_error()
        survival_prob = 1 - total_error
        T = math.ceil(key_len / survival_prob)

        sender, receiver = self.endpoints
        send_time = sender.calc_total_send_delay(T)
        recv_time = receiver.calc_total_receive_delay(T)
        prop_delay = self.length / self.fiber_speed

        total_time = send_time + recv_time + 2 * prop_delay

        return {
            "qubits_needed": T,
            "total_time_seconds": total_time,
            "qubit_loss_rate": total_error,
        }

    def run_for(self, key_len, time):
        total_error = self.get_total_error()
        survival_prob = 1 - total_error
        T = math.ceil(key_len / survival_prob)

        sender, receiver = self.endpoints
        prop_delay = self.length / self.fiber_speed

        per_qubit_time = (
            sender.calc_total_send_delay(1)
            + receiver.calc_total_receive_delay(1)
            + 2 * prop_delay
        )

        max_qubits = int(time // per_qubit_time)
        expected_key_length = int(max_qubits * survival_prob)

        return {
            "qubits_needed": T,
            "qubits_possible": max_qubits,
            "key_generated": expected_key_length,
            "qubit_loss_rate": total_error,
        }

    def estimateKeyGenerationTime(self, key_len):
        """
        Estimate the time required to generate a key of the specified length,
        including all delays and error rates.
        """
        total_success = 1.0
        for err in self.error_sources.values():
            total_success *= 1 - err
        total_error = 1 - total_success

        survival_prob = 1 - total_error
        # Estimate how many qubits need to be sent to generate the desired key length
        T = math.ceil(key_len / survival_prob)

        # Calculate time for sending and receiving the qubits
        sender, receiver = self.endpoints
        send_time = sender.calc_total_send_delay(T)
        recv_time = receiver.calc_total_receive_delay(T)

        # Propagation delay over the fiber (2-way propagation)
        prop_delay = self.length / self.fiber_speed

        # Total time estimate
        total_time = send_time + recv_time + 2 * prop_delay

        return {
            "total_time_seconds": total_time,
            "qubits_needed": T,
            "qubit_loss_rate": total_error,
        }


class Endpoint:
    def __init__(
        self,
        transmission_delay_per_qubit=0.0,
        processing_delay_per_qubit=0.0,
        fixed_delay=0.0,
    ):
        """
        Parameters:
        - transmission_delay_per_qubit (float): Delay (seconds) to transmit each qubit
        - processing_delay_per_qubit (float): Delay (seconds) to process each qubit
        - fixed_delay (float): Fixed overhead delay (seconds) per operation (send or receive)
        """
        self.transmission_delay_per_qubit = transmission_delay_per_qubit
        self.processing_delay_per_qubit = processing_delay_per_qubit
        self.fixed_delay = fixed_delay

    def calc_total_send_delay(self, T):
        """
        Total delay to send T qubits, based on fixed + transmission + processing delays.
        """
        total_delay = (
            self.fixed_delay
            + T * self.transmission_delay_per_qubit
            + T * self.processing_delay_per_qubit
        )
        return total_delay

    def calc_total_receive_delay(self, T):
        """
        Total delay to receive T qubits, based on fixed + transmission + processing delays.
        """
        total_delay = T * (
            self.fixed_delay
            + self.transmission_delay_per_qubit
            + self.processing_delay_per_qubit
        )
        return total_delay


# Testing


def test_endpoint():
    print("=== Testing Endpoint ===")
    ep = Endpoint(
        transmission_delay_per_qubit=10e-6,
        processing_delay_per_qubit=20e-6,
        fixed_delay=5e-6,
    )

    T = 10
    send_delay = ep.calc_total_send_delay(T)
    recv_delay = ep.calc_total_receive_delay(T)

    print(f"Send delay for {T} qubits: {send_delay:.8f} s")
    print(f"Receive delay for {T} qubits: {recv_delay:.8f} s")


def test_simulator_basic_run():
    print("\n=== Testing Simulator.run ===")
    sender = Endpoint(10e-6, 20e-6, 5e-6)
    receiver = Endpoint(10e-6, 20e-6, 5e-6)

    sim = Simulator([sender, receiver], length=1000, len_err=0.00001, fiber_speed=2e8)
    sim.add_err_source("background_noise", 0.01)

    result = sim.run(key_len=100)

    print(f"Qubits needed: {result['qubits_needed']}")
    print(f"Total time: {result['total_time_seconds']:.8f} s")
    print(f"Qubit loss rate: {result['qubit_loss_rate']:.4%}")


def test_simulator_run_for():
    print("\n=== Testing Simulator.run_for ===")
    sender = Endpoint(10e-6, 20e-6, 5e-6)
    receiver = Endpoint(10e-6, 20e-6, 5e-6)

    sim = Simulator([sender, receiver], length=1000, len_err=0.00001, fiber_speed=2e8)
    sim.add_err_source("polarization_mismatch", 0.02)

    result = sim.run_for(key_len=200, time=0.01)

    print(f"Qubits needed: {result['qubits_needed']}")
    print(f"Qubits possible in time: {result['qubits_possible']}")
    print(f"Key generated: {result['key_generated']}")
    print(f"Qubit loss rate: {result['qubit_loss_rate']:.4%}")


def test_simulator_estimate_time():
    print("\n=== Testing Simulator.estimateKeyGenerationTime ===")
    sender = Endpoint(2e-6, 3e-6, 1e-6)
    receiver = Endpoint(2e-6, 3e-6, 1e-6)

    sim = Simulator([sender, receiver], length=2000, len_err=0.000015, fiber_speed=2e8)
    sim.add_err_source("dispersion", 0.015)

    result = sim.estimateKeyGenerationTime(key_len=500)

    print(f"Estimated time to generate key: {result['total_time_seconds']:.8f} s")
    print(f"Qubits needed: {result['qubits_needed']}")
    print(f"Qubit loss rate: {result['qubit_loss_rate']:.4%}")


def test_change_endpoints():
    print("\n=== Testing Simulator.change_endpoints ===")
    sender1 = Endpoint(1e-6, 1e-6, 1e-6)
    receiver1 = Endpoint(1e-6, 1e-6, 1e-6)

    sender2 = Endpoint(5e-6, 5e-6, 2e-6)
    receiver2 = Endpoint(5e-6, 5e-6, 2e-6)

    sim = Simulator([sender1, receiver1], length=3000, len_err=0.00001, fiber_speed=2e8)
    sim.add_err_source("fiber_bend", 0.01)

    result_before = sim.run(key_len=100)
    print(f"Before change - time: {result_before['total_time_seconds']:.8f} s")

    sim.change_endpoints([sender2, receiver2])
    result_after = sim.run(key_len=100)
    print(f"After change - time: {result_after['total_time_seconds']:.8f} s")


if __name__ == "__main__":
    test_endpoint()
    test_simulator_basic_run()
    test_simulator_run_for()
    test_simulator_estimate_time()
    test_change_endpoints()
