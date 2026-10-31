# Provide a standard PHP API for mounting React components

As part of migrating the Timeline block to React, the PHP code currently mounts the React component by manually generating the required HTML and serialising the component props.

For example:

{code:javascript}$props = json_encode($props, JSON_UNESCAPED_UNICODE | JSON_HEX_TAG);

$mount = html_writer::div('', '', [
    'data-react-component' => '@moodle/lms/block_timeline/Timeline',
    'data-react-props' => $props,
]);{code}

This exposes the implementation details of the React mounting mechanism to feature code. Consumers are required to understand:

*  the required {{data-*}} attributes; 
*  how props should be serialised; 
*  which JSON encoding options should be used; 
*  how the mount element should be constructed. 

This should instead be provided through a supported PHP API so that feature code only needs to specify the React component and its props. The implementation details of the mounting mechanism should remain internal to the frontend platform.

Providing a standard API would:

*  reduce boilerplate when creating React entry points; 
*  ensure consistent prop serialisation and escaping; 
*  hide the DOM contract used by the React autoinit system; 
*  allow the mounting implementation to evolve without requiring changes throughout core and plugins. 

The Timeline block can continue using the current approach until such an API is available, but future React components should be encouraged to use the new abstraction.

A new interface should also be considered to perform in a similar way as {{named_templatable}} to provide a simplified migration path from templates to React. This should allow the react component entrypoint to be generated based upon a renderable being rendered, for example:

{code:php}$renderable = new \block_timeline\output\main($sort, $filter, $limit);
$renderer = $this->page->get_renderer('block_timeline');
$this->content = (object) [
    'text' => $renderer->render($renderable),
    'footer' => '',
];{code}

The react interface should take precedence over the {{named_templatable}} interface, and have lower precedent than a specific {{render_[renderable]}} method.

*Acceptance criteria*

* A supported PHP API exists for mounting React components. 
* Feature code specifies only the component identifier and props. 
* Prop serialisation and escaping are handled internally.
* The DOM contract used by the React autoinit system is hidden from consumers. 
* Existing consumers can be migrated to the new API.
* A renderable react component interface exists.
** Which automatically handles rendering using the PHP API when a renderable is rendered using the {{render}} method
** Which has a higher precedent than {{named_templatable}}
** Which has a lower precedent than a correclty named {{render_[renderable_name]}} method in a renderer class.

The goal of this issue is not to change how React components are mounted, but to provide a stable abstraction over the current implementation so that feature and plugin developers are not coupled to its internal details.
