# Weight formats in model spec 0.4
## Common key word arguments for all weight formats
Optional arguments are marked as _optional_ or _optional*_ with an asterisk if they are optional depending on another argument's value.

- `source` _required_ URI or path to the weights file. Preferably a url.
- `attachments` _optional_ Dictionary of text keys and list values (that may contain any valid yaml) to additional, relevant files that are specific to the current weight format. A list of URIs can be listed under the `files` key to included additional files for generating the model package.
- `authors` _optional_ A list of authors. If this is the root weight (it does not have a `parent` field): the person(s) that have trained this model. If this is a child weight (it has a `parent` field): the person(s) who have converted the weights to this format.
- `parent` _optional_ The source weights used as input for converting the weights to this format. For example, if the weights were converted from the format `pytorch_state_dict` to `pytorch_script`, the parent is `pytorch_state_dict`. All weight entries except one (the initial set of weights resulting from training the model), need to have this field.
- `sha256` _optional_ SHA256 checksum of the source file specified. You can drag and drop your file to this [online tool](http://emn178.github.io/online-tools/sha256_checksum.html) to generate it in your browser. Or you can generate the SHA256 code for your model and weights by using for example, `hashlib` in Python. [here is a codesnippet](https://gist.github.com/FynnBe/e64460463df89439cff218bbf59c1100).

## Weight formats and their additional key word arguments
- `keras_hdf5` Keras HDF5 weights format
  - key word arguments:
    - `dependencies` _optional_ Dependency manager and dependency file, specified as `<dependency manager>:<relative path to file>`. For example: 'conda:./environment.yaml', 'maven:./pom.xml', or 'pip:./requirements.txt'. These dependencies are only used for the specified weight format.
    - `tensorflow_version` _optional_ 
- `onnx` ONNX weights format
  - key word arguments:
    - `dependencies` _optional_ Dependency manager and dependency file, specified as `<dependency manager>:<relative path to file>`. For example: 'conda:./environment.yaml', 'maven:./pom.xml', or 'pip:./requirements.txt'. These dependencies are only used for the specified weight format.
    - `opset_version` _optional_ 
- `pytorch_state_dict` PyTorch state dictionary weights format
  - key word arguments:
    - `architecture` _required_ Source code of the model architecture that either points to a local implementation: `<relative path to file>:<identifier of implementation within the file>` or the implementation in an available dependency: `<root-dependency>.<sub-dependency>.<identifier>`.
For example: `my_function.py:MyImplementation` or `bioimageio.core.some_module.some_class_or_function`.
    - `architecture_sha256` _optional*_ This field is only required if the architecture points to a source file. SHA256 checksum of the model source code file.You can drag and drop your file to this [online tool](http://emn178.github.io/online-tools/sha256_checksum.html) to generate it in your browser. Or you can generate the SHA256 code for your model and weights by using for example, `hashlib` in Python. [here is a codesnippet](https://gist.github.com/FynnBe/e64460463df89439cff218bbf59c1100).
    - `dependencies` _optional_ Dependency manager and dependency file, specified as `<dependency manager>:<relative path to file>`. For example: 'conda:./environment.yaml', 'maven:./pom.xml', or 'pip:./requirements.txt'. These dependencies are only used for the specified weight format.
    - `kwargs` _optional_ Keyword arguments for the implementation specified by `architecture`.
    - `pytorch_version` _optional_ 
- `tensorflow_js` Tensorflow Javascript weights format
  - key word arguments:
    - `dependencies` _optional_ Dependency manager and dependency file, specified as `<dependency manager>:<relative path to file>`. For example: 'conda:./environment.yaml', 'maven:./pom.xml', or 'pip:./requirements.txt'. These dependencies are only used for the specified weight format.
    - `tensorflow_version` _optional_ 
- `tensorflow_saved_model_bundle` Tensorflow Saved Model Bundle weights format
  - key word arguments:
    - `dependencies` _optional_ Dependency manager and dependency file, specified as `<dependency manager>:<relative path to file>`. For example: 'conda:./environment.yaml', 'maven:./pom.xml', or 'pip:./requirements.txt'. These dependencies are only used for the specified weight format.
    - `tensorflow_version` _optional_ 
- `torchscript` Torchscript weights format
  - key word arguments:
    - `dependencies` _optional_ Dependency manager and dependency file, specified as `<dependency manager>:<relative path to file>`. For example: 'conda:./environment.yaml', 'maven:./pom.xml', or 'pip:./requirements.txt'. These dependencies are only used for the specified weight format.
    - `pytorch_version` _optional_ 