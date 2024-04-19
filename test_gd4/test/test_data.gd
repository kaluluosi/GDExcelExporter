class_name TestData
extends GdUnitTestSuite

var True = true
var False = false

func test_data():
	var data = Settings.demo.data[1]
	
	assert_int(data.id).is_equal(1)
	assert_int(data._int).is_equal(1)
	assert_that(data._float).is_equal(1)
	assert_str(data._string).is_equal('恭喜你！成功配置好了Godot导表项目。')
	assert_bool(data._bool).is_true()
	assert_array(data._array).is_equal([1, 2, 3, 4, 5])
	assert_array(data._array_str).is_equal(['a', 'b', 'c'])
	assert_array(data._array_bool).is_equal([true, false])
	assert_dict(data._dict).is_equal({'name': 'Tom', 'age': 10})
	assert_str(data._tr_string).is_equal("这段话需要翻译")
	assert_array(data._tr_array_str).is_equal(["a","b","c"])
	assert_dict(data._tr_dict).is_equal({'name': 'Tom', 'age': 10})
	await assert_func(Settings.demo,"_function_1",["helloworld"]).is_equal("helloworld")
	await assert_func(Settings.demo,"_function_params_1",[1,2,3]).is_equal([1,2,3])
	
	var ret = data._function.call("helloworld")
	assert_str(ret).is_equal("helloworld")
	
	ret = data._function_params.call(1,2,3)
	assert_array(ret).is_equal([1,2,3])
