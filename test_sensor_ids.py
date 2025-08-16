from src.data.generator import DataGenerator, SensorNetwork


def test_sensor_ids_normalized():
    network = SensorNetwork(location="Alice Springs")
    generator = DataGenerator(network)

    assert generator.temperature_sensor.sensor_id == "temp_alice_springs"
    assert generator.pressure_sensor.sensor_id == "pressure_alice_springs"
    assert generator.humidity_sensor.sensor_id == "humidity_alice_springs"
