# BioImage.IO Model Resource Description File Specification 0.3.6
This specification defines the fields used in a BioImage.IO-compliant resource description file (`RDF`) for describing AI models with pretrained weights.
These fields are typically stored in YAML files which we called Model Resource Description Files or `model RDF`.
The model RDFs can be downloaded or uploaded to the bioimage.io website, produced or consumed by BioImage.IO-compatible consumers(e.g. image analysis software or other website).

The model RDF YAML file contains mandatory and optional fields. In the following description, optional fields are indicated by _optional_.
_optional*_ with an asterisk indicates the field is optional depending on the value in another field.

* <a id="format_version"></a>`format_version` _(required String)_ Version of the BioImage.IO Model Resource Description File Specification used.
This is mandatory, and important for the consumer software to verify before parsing the fields.
The recommended behavior for the implementation is to keep backward compatibility and throw an error if the model yaml
is in an unsupported format version. The current format version described here is
0.3.6
* <a id="authors"></a>`authors` _(required List\[Author\])_ A list of authors. The authors are the creators of the specifications and the primary points of contact.
  1. _(Author)_   is a Dict with the following keys:
  * <a id="authors:affiliation"></a>`affiliation` _(String)_ Affiliation.
  * <a id="authors:email"></a>`email` _(Email)_ 
  * <a id="authors:github_user"></a>`github_user` _(String)_ GitHub user name.
  * <a id="authors:name"></a>`name` _(String)_ Full name.
  * <a id="authors:orcid"></a>`orcid` _(String)_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
* <a id="cite"></a>`cite` _(required List\[CiteEntry\])_ A list of citation entries.
Each entry contains a mandatory `text` field and either one or both of `doi` and `url`.
E.g. the citation for the model architecture and/or the training data used.
  1. _(CiteEntry)_   is a Dict with the following keys:
  * <a id="cite:text"></a>`text` _(String)_ 
  * <a id="cite:doi"></a>`doi` _(DOI→String)_ 
  * <a id="cite:url"></a>`url` _(String)_ 
* <a id="description"></a>`description` _(required String)_ A string containing a brief description.
* <a id="license"></a>`license` _(required String)_ A [SPDX license identifier](https://spdx.org/licenses/)(e.g. `CC-BY-4.0`, `MIT`, `BSD-2-Clause`). We don't support custom license beyond the SPDX license list, if you need that please send an Github issue to discuss your intentions with the community.
* <a id="name"></a>`name` _(required String)_ Name of this model. It should be human-readable and only contain letters, numbers, `_`, `-` or spaces and not be longer than 36 characters.
* <a id="test_inputs"></a>`test_inputs` _(required List\[Union\[URI→String | RelativeLocalPath→Path\]\])_ List of URIs or local relative paths to test inputs as described in inputs for **a single test case**. This means if your model has more than one input, you should provide one URI for each input.Each test input should be a file with a ndarray in [numpy.lib file format](https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html#module-numpy.lib.format).The extension must be '.npy'.
* <a id="test_outputs"></a>`test_outputs` _(required List\[Union\[URI→String | RelativeLocalPath→Path\]\])_ Analog to to test_inputs.
* <a id="timestamp"></a>`timestamp` _(required DateTime)_ Timestamp of the initial creation of this model in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format.
* <a id="type"></a>`type` _(required String)_ 
* <a id="weights"></a>`weights` _(required Dict\[String, Union\[PytorchStateDictWeightsEntry | PytorchScriptWeightsEntry | KerasHdf5WeightsEntry | TensorflowJsWeightsEntry | TensorflowSavedModelBundleWeightsEntry | OnnxWeightsEntry\]\])_ The weights for this model. Weights can be given for different formats, but should otherwise be equivalent. The available weight formats determine which consumers can use this model.
  1. _(String)_ Format of this set of weights. Weight formats can define additional (optional or required) fields. See [weight_formats_spec_0_3.md](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/weight_formats_spec_0_3.md). One of: pytorch_state_dict, pytorch_script, keras_hdf5, tensorflow_js, tensorflow_saved_model_bundle, onnx
* <a id="attachments"></a>`attachments` _(optional Attachments)_ Additional unknown keys are allowed. Attachments is a Dict with the following keys:
  * <a id="attachments:files"></a>`files` _(optional List\[Union\[URI→String | RelativeLocalPath→Path\]\])_ File attachments; included when packaging the resource.
* <a id="badges"></a>`badges` _(optional List\[Badge\])_ a list of badges
  1. _(Badge)_ Custom badge. Badge is a Dict with the following keys:Custom badge.
  * <a id="badges:label"></a>`label` _(String)_ e.g. 'Open in Colab'
  * <a id="badges:icon"></a>`icon` _(String)_ e.g. 'https://colab.research.google.com/assets/colab-badge.svg'
* <a id="config"></a>`config` _(optional YamlDict→Dict\[Any, Any\])_ A custom configuration field that can contain any keys not present in the RDF spec. This means you should not store, for example, github repo URL in `config` since we already have the `git_repo` key defined in the spec.
Keys in `config` may be very specific to a tool or consumer software. To avoid conflicted definitions, it is recommended to wrap configuration into a sub-field named with the specific domain or tool name, for example:
    ```yaml
       config:
          bioimage_io:  # here is the domain name
            my_custom_key: 3837283
            another_key:
               nested: value
          imagej:
            macro_dir: /path/to/macro/file
    ```
    If possible, please use [`snake_case`](https://en.wikipedia.org/wiki/Snake_case) for keys in `config`.

    For example:
    ```yaml
    config:
      # custom config for DeepImageJ, see https://github.com/bioimage-io/configuration/issues/23
      deepimagej:
        model_keys:
          # In principle the tag "SERVING" is used in almost every tf model
          model_tag: tf.saved_model.tag_constants.SERVING
          # Signature definition to call the model. Again "SERVING" is the most general
          signature_definition: tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY
        test_information:
          input_size: [2048x2048] # Size of the input images
          output_size: [1264x1264 ]# Size of all the outputs
          device: cpu # Device used. In principle either cpu or GPU
          memory_peak: 257.7 Mb # Maximum memory consumed by the model in the device
          runtime: 78.8s # Time it took to run the model
          pixel_size: [9.658E-4µmx9.658E-4µm] # Size of the pixels of the input
    ```

* <a id="covers"></a>`covers` _(optional List\[Union\[URL→URI | RelativeLocalPath→Path\]\])_ A list of cover images provided by either a relative path to the model folder, or a hyperlink starting with 'http[s]'. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1. The supported image formats are: 'jpg', 'png', 'gif'.
* <a id="dependencies"></a>`dependencies` _(optional Dependencies→String)_ Dependency manager and dependency file, specified as `<dependency manager>:<relative path to file>`. For example: 'conda:./environment.yaml', 'maven:./pom.xml', or 'pip:./requirements.txt'
* <a id="download_url"></a>`download_url` _(optional URL→URI)_ optional url to download the resource from
* <a id="framework"></a>`framework` _(optional String)_ The deep learning framework of the source code. One of: pytorch, tensorflow. This field is only required if the field `source` is present.
* <a id="git_repo"></a>`git_repo` _(optional String)_ A url to the git repository, e.g. to Github or Gitlab.If the model is contained in a subfolder of a git repository, then a url to the exact folder(which contains the configuration yaml file) should be used.
* <a id="icon"></a>`icon` _(optional String)_ an icon for the resource
* <a id="id"></a>`id` _(optional String)_ Unique id within a collection of resources.
* <a id="inputs"></a>`inputs` _(optional List\[InputTensor\])_ Describes the input tensors expected by this model.
  1. _(InputTensor)_   is a Dict with the following keys:
  * <a id="inputs:axes"></a>`axes` _(Axes→String)_ Axes identifying characters from: bitczyx. Same length and order as the axes in `shape`.

    | character | description |
    | --- | --- |
    |  b  |  batch (groups multiple samples) |
    |  i  |  instance/index/element |
    |  t  |  time |
    |  c  |  channel |
    |  z  |  spatial dimension z |
    |  y  |  spatial dimension y |
    |  x  |  spatial dimension x |
  * <a id="inputs:data_type"></a>`data_type` _(String)_ The data type of this tensor. For inputs, only `float32` is allowed and the consumer software needs to ensure that the correct data type is passed here. For outputs can be any of `float32, float64, (u)int8, (u)int16, (u)int32, (u)int64`. The data flow in bioimage.io models is explained [in this diagram.](https://docs.google.com/drawings/d/1FTw8-Rn6a6nXdkZ_SkMumtcjvur9mtIhRqLwnKqZNHM/edit).
  * <a id="inputs:name"></a>`name` _(String)_ Tensor name.
    * _(ExplicitShape→List\[Integer\])_ Exact shape with same length as `axes`, e.g. `shape: [1, 512, 512, 1]`
    * _(ParametrizedInputShape)_ A sequence of valid shapes given by `shape = min + k * step for k in {0, 1, ...}`. ParametrizedInputShape is a Dict with the following keys:
    * <a id="inputs:min"></a>`min` _(List\[Integer\])_ The minimum input shape with same length as `axes`
    * <a id="inputs:step"></a>`step` _(List\[Integer\])_ The minimum shape change with same length as `axes`
  * <a id="inputs:data_range"></a>`data_range` _(Tuple)_ Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor. If not specified, the full data range that can be expressed in `data_type` is allowed.
  * <a id="inputs:description"></a>`description` _(String)_ 
  * <a id="inputs:preprocessing"></a>`preprocessing` _(List\[Preprocessing\])_ Description of how this input should be preprocessed.
    1. _(Preprocessing)_   is a Dict with the following keys:
    * <a id="inputs:preprocessing:name"></a>`name` _(String)_ Name of preprocessing. One of: binarize, clip, scale_linear, sigmoid, zero_mean_unit_variance, scale_range.
    * <a id="inputs:preprocessing:kwargs"></a>`kwargs` _(Kwargs→Dict\[String, Any\])_ Key word arguments as described in [preprocessing spec](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/preprocessing_spec_0_3.md).
* <a id="kwargs"></a>`kwargs` _(optional Kwargs→Dict\[String, Any\])_ Keyword arguments for the implementation specified by `source`. This field is only required if the field `source` is present.
* <a id="language"></a>`language` _(optional* String)_ Programming language of the source code. One of: python, java. This field is only required if the field `source` is present.
* <a id="links"></a>`links` _(optional List\[String\])_ links to other bioimage.io resources
* <a id="maintainers"></a>`maintainers` _(optional List\[Maintainer\])_ Maintainers of this resource.
  1. _(Maintainer)_   is a Dict with the following keys:
  * <a id="maintainers:affiliation"></a>`affiliation` _(String)_ Affiliation.
  * <a id="maintainers:email"></a>`email` _(Email)_ 
  * <a id="maintainers:github_user"></a>`github_user` _(String)_ GitHub user name.
  * <a id="maintainers:name"></a>`name` _(String)_ Full name.
  * <a id="maintainers:orcid"></a>`orcid` _(String)_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
* <a id="outputs"></a>`outputs` _(optional List\[OutputTensor\])_ Describes the output tensors from this model.
  1. _(OutputTensor)_   is a Dict with the following keys:
  * <a id="outputs:axes"></a>`axes` _(Axes→String)_ Axes identifying characters from: bitczyx. Same length and order as the axes in `shape`.

    | character | description |
    | --- | --- |
    |  b  |  batch (groups multiple samples) |
    |  i  |  instance/index/element |
    |  t  |  time |
    |  c  |  channel |
    |  z  |  spatial dimension z |
    |  y  |  spatial dimension y |
    |  x  |  spatial dimension x |
  * <a id="outputs:data_type"></a>`data_type` _(String)_ The data type of this tensor. For inputs, only `float32` is allowed and the consumer software needs to ensure that the correct data type is passed here. For outputs can be any of `float32, float64, (u)int8, (u)int16, (u)int32, (u)int64`. The data flow in bioimage.io models is explained [in this diagram.](https://docs.google.com/drawings/d/1FTw8-Rn6a6nXdkZ_SkMumtcjvur9mtIhRqLwnKqZNHM/edit).
  * <a id="outputs:name"></a>`name` _(String)_ Tensor name.
    * _(ImplicitOutputShape)_ In reference to the shape of an input tensor, the shape of the output tensor is `shape = shape(input_tensor) * scale + 2 * offset`. ImplicitOutputShape is a Dict with the following keys:
    * <a id="outputs:offset"></a>`offset` _(List\[Float\])_ Position of origin wrt to input. Multiple of 0.5.
    * <a id="outputs:reference_tensor"></a>`reference_tensor` _(String)_ Name of the reference tensor.
    * <a id="outputs:scale"></a>`scale` _(List\[Float\])_ 'output_pix/input_pix' for each dimension.
  * <a id="outputs:data_range"></a>`data_range` _(Tuple)_ Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor. If not specified, the full data range that can be expressed in `data_type` is allowed.
  * <a id="outputs:description"></a>`description` _(String)_ 
  * <a id="outputs:halo"></a>`halo` _(List\[Integer\])_ Hint to describe the potentially corrupted edge region of the output tensor, due to boundary effects. The `halo` is not cropped by the bioimage.io model, but is left to be cropped by the consumer software. An example implementation of prediction with tiling, accounting for the halo can be found [here](https://github.com/bioimage-io/core-bioimage-io-python/blob/main/bioimageio/core/prediction.py#L195-L243). Use `shape:offset` if the model output itself is cropped and input and output shapes not fixed. 
  * <a id="outputs:postprocessing"></a>`postprocessing` _(List\[Postprocessing\])_ Description of how this output should be postprocessed.
    1. _(Postprocessing)_   is a Dict with the following keys:
    * <a id="outputs:postprocessing:name"></a>`name` _(String)_ Name of postprocessing. One of: binarize, clip, scale_linear, sigmoid, zero_mean_unit_variance, scale_range, scale_mean_variance.
    * <a id="outputs:postprocessing:kwargs"></a>`kwargs` _(Kwargs→Dict\[String, Any\])_ Key word arguments as described in [postprocessing spec](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/postprocessing_spec_0_3.md).
* <a id="packaged_by"></a>`packaged_by` _(optional List\[Author\])_ The persons that have packaged and uploaded this model. Only needs to be specified if different from `authors` in root or any entry in `weights`.
  1. _(Author)_   is a Dict with the following keys:
  * <a id="packaged_by:affiliation"></a>`affiliation` _(String)_ Affiliation.
  * <a id="packaged_by:email"></a>`email` _(Email)_ 
  * <a id="packaged_by:github_user"></a>`github_user` _(String)_ GitHub user name.
  * <a id="packaged_by:name"></a>`name` _(String)_ Full name.
  * <a id="packaged_by:orcid"></a>`orcid` _(String)_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
* <a id="parent"></a>`parent` _(optional ModelParent)_ Parent model from which the trained weights of this model have been derived, e.g. by finetuning the weights of this model on a different dataset. For format changes of the same trained model checkpoint, see `weights`. ModelParent is a Dict with the following keys:
  * <a id="parent:sha256"></a>`sha256` _(optional SHA256→String)_ Hash of the parent model RDF.
* <a id="run_mode"></a>`run_mode` _(optional RunMode)_ Custom run mode for this model: for more complex prediction procedures like test time data augmentation that currently cannot be expressed in the specification. No standard run modes are defined yet. RunMode is a Dict with the following keys:
  * <a id="run_mode:name"></a>`name` _(required String)_ The name of the `run_mode`
  * <a id="run_mode:kwargs"></a>`kwargs` _(optional Kwargs→Dict\[String, Any\])_ Key word arguments.
* <a id="sample_inputs"></a>`sample_inputs` _(optional List\[Union\[URI→String | RelativeLocalPath→Path\]\])_ List of URIs/local relative paths to sample inputs to illustrate possible inputs for the model, for example stored as png or tif images. The model is not tested with these sample files that serve to inform a human user about an example use case.
* <a id="sample_outputs"></a>`sample_outputs` _(optional List\[Union\[URI→String | RelativeLocalPath→Path\]\])_ List of URIs/local relative paths to sample outputs corresponding to the `sample_inputs`.
* <a id="sha256"></a>`sha256` _(optional String)_ SHA256 checksum of the model source code file.You can drag and drop your file to this [online tool](http://emn178.github.io/online-tools/sha256_checksum.html) to generate it in your browser. Or you can generate the SHA256 code for your model and weights by using for example, `hashlib` in Python. [here is a codesnippet](https://gist.github.com/FynnBe/e64460463df89439cff218bbf59c1100). This field is only required if the field source is present.
* <a id="source"></a>`source` _(optional* ImportableSource→String)_ Language and framework specific implementation. As some weights contain the model architecture, the source is optional depending on the present weight formats. `source` can either point to a local implementation: `<relative path to file>:<identifier of implementation within the source file>` or the implementation in an available dependency: `<root-dependency>.<sub-dependency>.<identifier>`.
For example: `my_function.py:MyImplementation` or `core_library.some_module.some_function`.
* <a id="tags"></a>`tags` _(optional List\[String\])_ A list of tags.
* <a id="version"></a>`version` _(optional StrictVersion→String)_ The version number of the model. The version number format must be a string in `MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/), e.g. the initial version number should be `0.1.0`.