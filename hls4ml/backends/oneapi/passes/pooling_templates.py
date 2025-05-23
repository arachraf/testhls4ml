from hls4ml.backends.oneapi.oneapi_template import StreamFunctionCallTemplate, TaskSequenceTemplate
from hls4ml.backends.template import FunctionCallTemplate, LayerConfigTemplate
from hls4ml.model.layers import GlobalPooling1D, GlobalPooling2D, Pooling1D, Pooling2D

pooling1d_config_template = """struct config{index} : nnet::pooling1d_config {{
    static const unsigned stride_width = {stride_width};
    static const unsigned pool_width = {pool_width};

    static const unsigned n_in = {n_in};
    static const unsigned n_out = {n_out};
    static const unsigned filt_width = {pool_width};

    static const unsigned n_filt = {n_filt};
    static const unsigned n_chan = {n_filt};

    static const unsigned in_width = {n_in};

    static const unsigned pad_left = {pad_left};
    static const unsigned pad_right = {pad_right};
    static const bool count_pad = {count_pad};

    static const nnet::Pool_Op pool_op = nnet::{pool_op};
    typedef {accum_t.name} accum_t;
}};\n"""

pooling2d_config_template = """struct config{index} : nnet::pooling2d_config {{
    static const unsigned stride_height = {stride_height};
    static const unsigned stride_width = {stride_width};

    static const unsigned pool_height = {pool_height};
    static const unsigned pool_width = {pool_width};
    static const unsigned filt_height = {pool_height};
    static const unsigned filt_width = {pool_width};

    static const unsigned in_height = {in_height};
    static const unsigned in_width = {in_width};
    static const unsigned out_height = {out_height};
    static const unsigned out_width = {out_width};

    static const unsigned n_filt = {n_filt};
    static const unsigned n_chan = {n_filt};

    static const unsigned pad_top = {pad_top};
    static const unsigned pad_bottom = {pad_bottom};
    static const unsigned pad_left = {pad_left};
    static const unsigned pad_right = {pad_right};
    static const bool count_pad = {count_pad};

    static const nnet::Pool_Op pool_op = nnet::{pool_op};
    typedef {accum_t.name} accum_t;
}};\n"""

global_pooling1d_config_template = """struct config{index} : nnet::pooling1d_config {{
    static const unsigned n_in = {n_in};
    static const unsigned n_filt = {n_filt};
    static const nnet::Pool_Op pool_op = nnet::{pool_op};
    typedef {accum_t.name} accum_t;
}};\n"""

global_pooling2d_config_template = """struct config{index} : nnet::pooling2d_config {{
    static const unsigned in_height = {in_height};
    static const unsigned in_width = {in_width};
    static const unsigned n_filt = {n_filt};
    static const nnet::Pool_Op pool_op = nnet::{pool_op};
    typedef {accum_t.name} accum_t;
}};\n"""

pooling1d_function_template = 'nnet::pooling1d_{data_format}<{input_t}, {output_t}, {config}>({input}, {output});'
pooling2d_function_template = 'nnet::pooling2d_{data_format}<{input_t}, {output_t}, {config}>({input}, {output});'
global_pooling1d_function_template = (
    'nnet::global_pooling1d_{data_format}<{input_t}, {output_t}, {config}>({input}, {output});'
)
global_pooling2d_function_template = (
    'nnet::global_pooling2d_{data_format}<{input_t}, {output_t}, {config}>({input}, {output});'
)

pooling1d_task_sequence_template = (
    'task_sequence<nnet::pooling1d_{data_format}_stream<{input_pipe}, {output_pipe}, {config}>>({name});'
)
pooling2d_task_sequence_template = (
    'task_sequence<nnet::pooling2d_{data_format}_stream<{input_pipe}, {output_pipe}, {config}>>({name});'
)
global_pooling1d_task_sequence_template = (
    'task_sequence<nnet::global_pooling1d_{data_format}_stream<{input_pipe}, {output_pipe}, {config}>>({name});'
)
global_pooling2d_task_sequence_template = (
    'task_sequence<nnet::global_pooling2d_{data_format}_stream<{input_pipe}, {output_pipe}, {config}>>({name});'
)

pooling_stream_function_template = '{name}.async();'

pooling_include_list = ['nnet_utils/nnet_pooling.h', 'nnet_utils/nnet_pooling_stream.h']


class PoolingConfigTemplate(LayerConfigTemplate):
    def __init__(self):
        super().__init__((Pooling1D, Pooling2D, GlobalPooling1D, GlobalPooling2D))
        self.templates = {
            'Pooling1D': pooling1d_config_template,
            'Pooling2D': pooling2d_config_template,
            'GlobalPooling1D': global_pooling1d_config_template,
            'GlobalPooling2D': global_pooling2d_config_template,
        }

    def format(self, node):
        params = self._default_config_params(node)
        return self.templates[node.class_name].format(**params)


class PoolingFunctionTemplate(FunctionCallTemplate):
    def __init__(self):
        super().__init__((Pooling1D, Pooling2D, GlobalPooling1D, GlobalPooling2D), include_header=pooling_include_list)
        self.templates = {
            'Pooling1D': pooling1d_function_template,
            'Pooling2D': pooling2d_function_template,
            'GlobalPooling1D': global_pooling1d_function_template,
            'GlobalPooling2D': global_pooling2d_function_template,
        }

    def format(self, node):
        params = self._default_function_params(node)
        if node.get_attr('data_format') == 'channels_first':
            raise Exception('channels_first not supported for oneAPI')
        params['data_format'] = 'cl'
        return self.templates[node.class_name].format(**params)


class PoolingTaskSequenceTemplate(TaskSequenceTemplate):
    def __init__(self):
        super().__init__((Pooling1D, Pooling2D, GlobalPooling1D, GlobalPooling2D))
        self.templates = {
            'Pooling1D': pooling1d_task_sequence_template,
            'Pooling2D': pooling2d_task_sequence_template,
            'GlobalPooling1D': global_pooling1d_task_sequence_template,
            'GlobalPooling2D': global_pooling2d_task_sequence_template,
        }

    def format(self, node):
        params = self._default_function_params(node)
        if node.get_attr('data_format') == 'channels_first':
            raise Exception('channels_first not supported for oneAPI')
        params['data_format'] = 'cl'
        return self.templates[node.class_name].format(**params)


class PoolingStreamFunctionTemplate(StreamFunctionCallTemplate):
    def __init__(self):
        super().__init__((Pooling1D, Pooling2D, GlobalPooling1D, GlobalPooling2D))
        self.template = pooling_stream_function_template

    def format(self, node):
        params = self._default_function_params(node)
        return self.template.format(**params)
