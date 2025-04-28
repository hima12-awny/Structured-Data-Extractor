import json
import streamlit as st
from time import sleep


class MultiSchemaJSONConverter:
    def __init__(self):
        self.schemas = st.session_state.get('schemas', [])

        self.load_schemas_from_json()
        self.render()

    def render(self):
        st.header("Make & Set Response Formatter")

        # Initialize session state for schemas
        if 'schemas' not in st.session_state:
            st.session_state.schemas = []

        if 'stored_schemas' not in st.session_state:
            st.session_state.stored_schemas = dict()

        # Display each schema
        for schema_index, schema in enumerate(st.session_state.schemas):
            with st.container(border=True):
                header = st.empty()
                header.header(f"Schema {schema_index + 1}")

                new_old_schema = st.selectbox(
                    label=f"Select Stored Schema or New One ({schema_index+1})",
                    options=["New Schema"] +
                    list(st.session_state.stored_schemas)
                )

                if new_old_schema not in ["New Schema", schema['title']]:
                    schema = st.session_state.stored_schemas[new_old_schema]
                    st.session_state.schemas[schema_index] = schema

                # Input for schema name
                cols = st.columns([4, 1], vertical_alignment='bottom')

                schema['title'] = cols[0].text_input(
                    f"Schema ({schema_index + 1}) Name",
                    value=schema['title'],
                    key=f"schema_name_{schema_index}"
                )

                if schema['title']:
                    header.header(f"Schema ({schema['title']})")

                schema["set_response_formate"] = cols[1].checkbox(
                    "Set As Response Formatter",
                    key=f"set_as_response_schema_{schema_index}",
                    value=schema["set_response_formate"])

                # Collect existing schema names for type options, excluding the current schema's name
                existing_schema_names = [
                    s['title']
                    for i, s in enumerate(st.session_state.schemas)
                    if s['title'] and i != schema_index
                ]

                # Define basic types and extended types
                basic_types = [
                    "string", "integer", "float",
                    "boolean", "array", "enum"
                ]
                extended_types = basic_types + existing_schema_names

                num_fields = len(schema['properties'])
                expander = st.expander(
                    f"Fields ({num_fields}):", expanded=True)
                # Display fields for the current schema
                for i, field in enumerate(schema['properties']):
                    with expander.container(border=True):
                        st.subheader(f"Field {i+1}")

                        cols = st.columns([4, 1], vertical_alignment='bottom')

                        field['title'] = cols[0].text_input(
                            f"Name",
                            value=field.get('title', ''),
                            key=f"name_{schema_index}_{i}",
                        )

                        field['required'] = cols[1].checkbox(f"Required", value=field.get(
                            'required', True),
                            key=f"required_{schema_index}_{i}",
                        )

                        # Layout for type selection
                        col1, col2 = st.columns([1, 1])

                        type_index = 0
                        if field['type'] in extended_types:
                            type_index = extended_types.index(field['type'])

                        with col1:
                            field['type'] = st.selectbox(
                                f"Type",
                                options=extended_types,
                                index=max(type_index, 0),
                                key=f"type_{schema_index}_{i}"
                            )

                        with col2:
                            types_without_array = extended_types.copy()
                            if 'array' in types_without_array:
                                types_without_array.remove('array')
                                types_without_array.remove('enum')

                            # Only show items type if array is selected
                            if field['type'] == 'array':
                                items_type_index = 0
                                if 'items' in field and 'type' in field['items'] and field['items']['type'] in types_without_array:
                                    items_type_index = types_without_array.index(
                                        field['items']['type'])

                                if 'items' not in field:
                                    field['items'] = {'type': None}

                                field['items']['type'] = st.selectbox(
                                    f"Items Type",
                                    options=types_without_array,
                                    index=max(items_type_index, 0),
                                    key=f"items_type_{schema_index}_{i}"
                                )
                            # Initialize enum values if not present
                            elif field['type'] == 'enum':
                                if 'enum_values' not in field:
                                    field['enum_values'] = []
                                if 'enum_type' not in field:
                                    field['enum_type'] = 'string'

                                field['enum_type'] = st.selectbox(
                                    "Enum Base Type",
                                    options=["string", "integer", "number"],
                                    index=0,
                                    key=f"enum_base_type_{schema_index}_{i}"
                                )

                        # Add description field
                        field['description'] = st.text_area(
                            f"Description",
                            value=field.get('description', ''),
                            key=f"description_{schema_index}_{i}",
                            placeholder="Optional"
                        )

                        # Enum values management section
                        if field['type'] == 'enum':
                            st.markdown("#### Enum Values")

                            # Add new enum value
                            new_value_col, add_btn_col = st.columns(
                                [3, 1], vertical_alignment='bottom',)

                            new_enum_value = new_value_col.text_input(
                                "Add new enum value",
                                key=f"new_enum_value_{schema_index}_{i}",
                                placeholder="Enter value and click Add"
                            )

                            if add_btn_col.button("Add", key=f"add_enum_value_{schema_index}_{i}", use_container_width=True):
                                # Convert value based on enum_type
                                try:
                                    if field['enum_type'] == 'integer':
                                        parsed_value = int(new_enum_value)
                                    elif field['enum_type'] == 'number':
                                        parsed_value = float(new_enum_value)
                                    else:  # default to string
                                        parsed_value = new_enum_value

                                    if new_enum_value:
                                        if parsed_value in field['enum_values']:
                                            st.info(
                                                "this Enum value exists in the list")

                                        else:
                                            field['enum_values'].append(
                                                parsed_value)
                                except ValueError:
                                    st.error(
                                        f"Invalid value for type {field['enum_type']}")

                            # Display current enum values with delete buttons
                            if field['enum_values']:
                                st.markdown("Current values:")

                                cols = st.columns(4, gap='small')
                                for enum_idx, enum_val in enumerate(field['enum_values']):
                                    col_idx = enum_idx % 4
                                    if cols[col_idx].button(f"❌ {enum_val}", key=f"remove_enum_{schema_index}_{i}_{enum_idx}", use_container_width=True):
                                        self.delete_enum_value(
                                            schema_index, i, enum_idx)
                                        st.rerun()

                        if st.columns([1, 1, 1])[2].button(
                            f"Delete Field",
                            key=f"delete_field_{schema_index}_{i}",
                            use_container_width=True
                        ):
                            self.delete_schema_field(
                                schema_index=schema_index, field_index=i)
                            st.rerun()

                cols = st.columns(2)

                if cols[0].button(
                    f"Add Field to Schema ({schema['title'] or schema_index+1})",
                    key=f"add_field_schema_{schema_index}",
                    use_container_width=True,
                        type='primary'):

                    schema['properties'].append(
                        {
                            "description": None,
                            "title": None,
                            "type": None,
                            "items": {"type": None},
                            "enum_values": []
                        }
                    )

                    st.rerun()

                btns_container = cols[1].popover(
                    f"Delete Schema ({schema['title'] or schema_index+1})", use_container_width=True)

                # Button to delete the current schema
                if btns_container.button(
                    f"only from this list",
                    key=f"delete_schema_{schema_index}_only_from_this_list",
                    use_container_width=True
                ):
                    self.delete_schema(schema_index)
                    st.rerun()

                if btns_container.button(
                    f"from this and stored list",
                    key=f"delete_schema_{schema_index}_from_list_and_stored",
                    use_container_width=True
                ):
                    self.delete_schema(schema_index)
                    self.delete_schema_form_stored(schema['title'])
                    self.save_schemas_in_json()
                    st.rerun()

        cols = st.columns([1.8, 2.5, 2, 1])

        # Button to add a new schema
        if cols[0].button("Add Schema", use_container_width=True, type='primary'):
            self.add_schema()
            st.rerun()

        # Generate JSON output
        if cols[1].button("Generate Formatter", use_container_width=True):

            final_response_schema = self.generate_json()

            if st.session_state.get("dev_mode"):

                @st.dialog("Response Formatter")
                def show_json():
                    st.json(final_response_schema)
                    if st.button("Set as Response Formatter", use_container_width=True, type='primary'):
                        st.session_state.final_response_schema = final_response_schema
                        st.success("✅ Response Formatter Set Successfully")
                        sleep(2)
                        st.rerun()
                        return

                show_json()

            else:
                st.session_state.final_response_schema = final_response_schema
                st.success("✅ Response Formatter Set Successfully")
                sleep(2)
                st.rerun()

        # Generate JSON output
        if cols[2].button("Save Schemas", use_container_width=True):

            if st.session_state.schemas:
                self.save_schemas_in_json()
                st.success("All Schemas Is Stored Successfully")

            else:
                st.error("Please add at least one schema.")
                st.stop()

        if cols[3].button("Clear", use_container_width=True):
            st.session_state.schemas = []
            st.rerun()

    def add_schema(self):
        st.session_state.schemas.append({
            "title": "",
            "properties": [],
            "type": "object",
            "required": [],
            "set_response_formate": False
        })

    def delete_schema(self, index):
        del st.session_state.schemas[index]

    def delete_schema_form_stored(self, title):
        if title in st.session_state.stored_schemas:
            del st.session_state.stored_schemas[title]

    def delete_schema_field(self, schema_index, field_index):
        del st.session_state.schemas[schema_index]["properties"][field_index]

    def delete_enum_value(self, schema_index, field_index, enum_index):
        st.session_state.schemas[schema_index]["properties"][field_index]["enum_values"].pop(
            enum_index)

    def save_schemas_in_json(self):

        for schema in st.session_state.schemas:
            if schema["title"].strip():
                st.session_state.stored_schemas[schema["title"]] = schema

        with open(r'schemas.json', 'w') as f:
            json.dump(st.session_state.stored_schemas, f, indent=2)

    def load_schemas_from_json(self):
        with open(r'schemas.json', 'r') as f:
            st.session_state.stored_schemas = json.loads(f.read())

    def generate_json(self):
        if not st.session_state.schemas:
            st.error("Please add at least one schema.")
            st.stop()

        if sum(
            schema.get("set_response_formate", False)
            for schema in st.session_state.schemas
        ) != 1:
            st.error("Exactly one schema should be set as Response Formatter.")
            st.stop()

        response_formatter_name = None
        for schema in st.session_state.schemas:
            if schema.get("set_response_formate", False):
                response_formatter_name = schema['title']

        schemas_names = set(s['title'] for s in st.session_state.schemas)

        all_schemas = {}
        included_schema = set()

        for schema_idx, schema in enumerate(st.session_state.schemas, 1):

            if not schema['title'].strip():
                st.error(f"Error while Schema ({schema_idx}) without Name")
                st.stop()

                break

            json_output = {
                "title": schema['title'],
                "type": schema['type'],
                "properties": dict(),
                "required": [],
                "set_response_formate": schema.get("set_response_formate", False)
            }

            for field_idx, field in enumerate(schema['properties']):

                field_name = field['title'].strip()

                if len(field_name) == 0:
                    st.error(
                        f"Error while if Schema {schema['title']} in Field ({field_idx}) without title")
                    st.stop()
                    break

                t = field['type']
                if t == 'float':
                    t = "number"

                # Handle enum type specially
                if t == 'enum':
                    base_type = field.get('enum_type', 'string')
                    if base_type == 'float':  # Normalize type names
                        base_type = 'number'

                    field_def = {
                        "type": base_type,
                        "enum": field.get('enum_values', [])
                    }
                elif t in schemas_names:
                    included_schema.add(t)
                    field_def = {
                        'type': {
                            '$ref': f'#/$defs/{t}'
                        }
                    }
                else:
                    field_def = {
                        "type": t,
                    }
                    field_def['title'] = field_name

                if field.get('description'):
                    field_def['description'] = field['description']

                if t == 'array' and 'items' in field:
                    items_t = field['items']['type']
                    if items_t == 'float':
                        items_t = "number"

                    if items_t == 'enum' and 'enum_values' in field['items']:
                        items_base_type = field['items'].get(
                            'enum_type', 'string')
                        if items_base_type == 'float':
                            items_base_type = 'number'

                        type_ = {
                            "type": items_base_type,
                            "enum": field['items']['enum_values']
                        }
                    elif items_t in schemas_names:
                        included_schema.add(items_t)
                        type_ = {
                            '$ref': f"#/$defs/{items_t}"
                        }
                    else:
                        type_ = {"type": items_t}

                    field_def["items"] = type_

                if field.get('required'):
                    json_output["required"].append(field_name)

                json_output["properties"][field_name] = field_def

            all_schemas[schema['title']] = json_output

        # st.subheader("All Schemas")
        # st.json(all_schemas)

        response_formatter = all_schemas[response_formatter_name]

        if included_schema:
            included_schemas_dict = {
                title: schema
                for title, schema in all_schemas.items()
                if title in included_schema  # Only include necessary schemas
            }

            for title in included_schemas_dict.keys():
                if "set_response_formate" in included_schemas_dict[title]:
                    del included_schemas_dict[title]["set_response_formate"]

            response_formatter["$defs"] = included_schemas_dict

        if "set_response_formate" in response_formatter:
            del response_formatter["set_response_formate"]

        return response_formatter
