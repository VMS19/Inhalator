from drivers.sfm3200_flow_sensor import Sfm3200
import logging


def main():
    logging.basicConfig(level=logging.DEBUG)
    sfm = Sfm3200()
    flow = sfm.read()
    print(flow)


if __name__ == "__main__":
    main()
