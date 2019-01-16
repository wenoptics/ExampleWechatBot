# ExampleWechatBot
Example project of [pyWechatBot](https://github.com/wenoptics/pyWechatProxyClient)

## Run
Simply `python3 main.py`

## Quick Start
It's easy to implement a new command:
```python
@wxbot.register_command("Hello", is_private=True)
def on_request_something(bot: CommandBot, msg, chat, reply,
                         some_of_your_extra_params="SomeDefaultValue", *args, **kwargs):

    print('in on_request_something() {} {} {}'
          .format(msg, chat, some_of_your_extra_params))

    # Extract your stuff from request input
    import re
    something = re.search(r'\w+', msg)
    if something:
        something = something.group(0)
    else:
        something = ''

    ret_msgs = "Hi {}, welcome".format(something)
    reply(ret_msgs)
```

And send "`#Hello` `Grayson`" on Wechat, it should reply 
> "Hi `Grayson`, welcome"



## Implementation
For command implementation, see [`./ExampleBusiness/ExampleCommands.py`](./ExampleBusiness/ExampleCommands.py)

For publish message implementation, see demo code in [`./ExampleBusiness/ExamplePublish.py`](./ExampleBusiness/ExamplePublish.py)

