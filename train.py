from voyager import Voyager

VOYAGER_KWARGS = {"mc_port": "",
                  "openai_api_key": ""}

voyager = Voyager(**VOYAGER_KWARGS)

# start lifelong learning
voyager.learn()
