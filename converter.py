from math import copysign
SYSTEM_RATIO_SCALE = 36.55


def pressure_to_flow(pressure_cmh2o):
    # Convert to flow value
    flow = (abs(pressure_cmh2o) ** 0.5) * SYSTEM_RATIO_SCALE

    # Add sign for flow direction
    if pressure_cmh2o < 0:
        flow = -flow

    return flow


def flow_to_pressure(flow):
    pressure = flow / SYSTEM_RATIO_SCALE
    return copysign(pressure ** 2, flow)
