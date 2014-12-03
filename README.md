
Todo
- USE UNDERSCORE FOR COMBINING WORDS! e.g
-- ec2_prices.py  
-- config_files.py  
-- spot_prices.py  
-- spot_instance  
- Replace print statements with proper logging debug/info/warn
- Define SUPPORTED_AMIS as parameter/settings
- Dynamically fetch SUPPORTED_INSTANCES from AWS
- [eu-ireland](https://github.com/screen6/spotprice/blob/master/spotprice/libs/ec2prices.py#L15)  is static. Make it a argument
- indicate that one must setup the [ec2.cfg](https://github.com/screen6/spotprice/blob/master/spotprice/libs/ec2.py#L10) file and make it an argument
- Replace https://github.com/screen6/spotprice/blob/master/spotprice/libs/securitygroups.py#L19 with logging statement ( Also you have to ```from __future__ import print_function``` for print function to work with paranthesis unless you're using Python 3. Support Python 2.x first of all.
- Don't use inline comments as much as possible. If something needs to be described, use the function documentation as follows


```python
def my_method(param1, param2):
  """This is a documentation line"""
  x = x ** 2
```
