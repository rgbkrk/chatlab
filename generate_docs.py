import inspect
import json
from typing import Dict, Any
import chatlab


def get_class_doc_info(cls):
    methods = inspect.getmembers(cls, predicate=inspect.isfunction)
    class_methods_info = []
    parent_classes = [c.__name__ for c in inspect.getmro(cls)[1:]]

    for method in methods:
        method_sig = inspect.signature(method[1])
        method_description = inspect.getdoc(method[1])
        return_annotation = inspect.signature(method[1]).return_annotation
        return_annotation = return_annotation.__name__ if inspect.isclass(return_annotation) else str(return_annotation) if return_annotation != inspect._empty else None
        
        parameters_info = []
        for param in method_sig.parameters.values():
            param_dict = {'name': param.name,
                          'default': param.default if param.default != param.empty else None,
                          'annotation': str(param.annotation) if param.annotation != param.empty else None}
            parameters_info.append(param_dict)
        
        method_info_dict = {'name': method[0],
                            'description': method_description,
                            'parameters': parameters_info,
                            'returns': return_annotation}
        class_methods_info.append(method_info_dict)
    
    return {
        "methods": class_methods_info,
        "parent_classes": parent_classes
    }


def gen_doc_info(module):
    classes = inspect.getmembers(module, predicate=inspect.isclass)
    module_doc_info = {}
    
    for cls in classes:
        class_name, class_obj = cls
        class_info = get_class_doc_info(class_obj)
        module_doc_info[class_name] = class_info
    
    return module_doc_info


def main():
    doc_info = gen_doc_info(chatlab)

    with open('website/docs/api/chatlab_doc.json', 'w') as fp:
        json.dump(doc_info, fp)

if __name__ == "__main__":
    main()
