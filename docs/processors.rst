==========
Processors
==========

Processors are used to further process an incoming file. This means it can
either replace the incoming file by a converted version (e.g. trim it) or
create additional versions of it which are saved as additional assets. The
latter is commonly used to create different sized version of an uploaded image.

Configuring a processor
=======================

In order to configure a processor on the uploader module you can use the following code::   

    modules = [
        upload_module(processors = [
                ImageResizer({
                        'thumb' : "50x",
                        'mini'  : "200x",
                        'height' : "x300",
                        'square' : "100x100!",
                        'square2' : "100x100"
                    },
                    original = "1000x1000",
                )]
            ]
        )
    }

As you can see you can give the upload module a list of processors which will then try to work on every
incoming file. The only provided processor is the ``ImageResizer`` right now which takes a dictionary
with name/imagesize mappings as it's input. 

The output of processor will be additional assets while optionally the original asset can be scaled as well.

Obtaining alternative versions of an asset
==========================================

As always you can request an asset from the upload module like this::

    asset = self.app.module_map.uploader.get(asset_id)

Now that you have the original asset you can access it's variations::

    thumbnail = asset.variants['thumbnail']

This will give you another asset which you can use as the original one, e.g. returning it::

    return thumbnail.get_fp()


Available Processors
====================

ImageResizer
------------

The ``ImageResizer`` will use the following syntax as it's input for image size definitions:

* ``50x`` means to use a width of 50 pixels and adjust the height according to the aspect ratio of the incoming image.
* ``x50`` means to use a height of 50 pixels and adjust the width according to the aspect ratio of the incoming image.
* ``50x50!`` means to scale the image to 50 width and height while ignoring the aspect ratio.
* ``50x50`` means the same but the aspect ratio will be used and portions of the image which do not fit will be cropped.

The optional ``original`` parameter will take an image size string as well and will replace the original asset with the 
processed version. If the parameter is not given or the input asset is no image then the original will not be touched.

