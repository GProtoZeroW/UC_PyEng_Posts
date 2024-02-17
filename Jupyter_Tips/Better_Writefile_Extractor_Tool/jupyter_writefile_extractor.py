#Exstracted from source notebook with relative path this files initial creation: ../Better_Jupyter_Writefile_Extractor_Tool_DevNB.ipynb


import os
from pathlib import Path
import json
import re
import warnings
from datetime import datetime



class Notebook_Writefile_Extractor:
    """
    The Notebook_Writefile_Extractor class is used for setting the files and paths 
    for the software.

    Args:
        file_and_paths_dict (dict): A dictionary containing the file names and corresponding paths.

    Attributes:
        file_and_paths_dict: A dictionary containing the file names and corresponding paths.

    Raises:
        AttributeError: If `self.find_writefile_in_cells` has not been run first to get `self._files_and_paths`.
        ValueError: If `file_and_paths_dict` is not a dictionary.
        ValueError: If `file_and_paths_dict` does not have the same keys as `self._files_and_paths`.
        ValueError: If `file_and_paths_dict` contains non pathlib Path object values for some keys.    
    """
    def __init__(self, notebook_path, default_output_path=Path.cwd()):
        """
        Construct an instance of the Notebook_Writefile_Extractor class.

        Args:
            notebook_path (:obj:`str`): The path to the jupyter notebook.
            default_output_path (:Path ob:`str`, optional; default=Path.cwd() current working directory): The default output
                directory for the files produced. Defaults to current working directory.
        """
        self.notebook_path=Path(notebook_path)
        self.notebook_path_check()
    
        self.default_output_path=Path(default_output_path)
        self.output_path_check(self.default_output_path)

        

        self.load_notebook()
        self.find_writefile_in_cells()

    def notebook_path_check(self):
        """
        Validates the notebook path.

        The method checks if the provided path is valid, is a file, is existing and has a suffix of ".ipynb" (i.e.,
        it is a Jupyter notebook file).

        Raises:
            ValueError: If the notebook path does not have a ".ipynb" suffix, is not a file or does not exist.
        """
        self.notebook_path=self.notebook_path.resolve(strict=True)

        if self.notebook_path.suffix != '.ipynb':
            raise ValueError(f'`{self.notebook_path =}` suffix is not `".ipynb"` and is therefore not a recognized ipython (jupyter) notebook file')
        
        if self.notebook_path.is_file() == False:
            raise ValueError(f'`{self.notebook_path =}` .is_file returned False and is therefore not a file')
        
        if self.notebook_path.exists() == False:
            raise ValueError(f'`{self.notebook_path =}` .exists returned False and is therefore not a exisiting file')

    def output_path_check(self, dir_path):
        """
        Validates the provided directory path.

        This method checks if the provided directory path is a valid output directory by making sure it is not a file
        or a symbolic link. If it is valid, the absolute path to it is returned.

        Args:
            dir_path (:obj:`str`): The path of the potential output directory.

        Returns:
             :Pathlib Path: The resolved absolute path of the directory.

        Raises:
            ValueError: If the directory path is a file or a symbolic link.
        """
        dir_path=Path(dir_path)
       
        dir_path=dir_path.resolve()
       

        if dir_path.is_file():
            raise ValueError(f"`{dir_path=}` was a file, not a potential directory")
        if dir_path.is_symlink():
            raise ValueError(f"`{dir_path=}` was a symlink, not a potential directory")

        return dir_path
        
            

    def load_notebook(self):
        """
        Load the notebook file into a JSON object.

        The method opens the notebook file specified by the notebook_path attribute, reads it and loads it into a
        JSON object which is then stored in the notebook_json attribute of the object.

        Note:


        Creates:
            self.notebook_json (json object): This method creates the self.notebook_json attribute.

        Returns:
            None

        Raises:
            FileNotFoundError: If the file specified by notebook_path does not exist.
            IOError: If the file cannot be opened for any reason.
            json.JSONDecodeError: If the file content is not valid JSON.
        """
        with self.notebook_path.open('r', encoding='utf-8') as nbfile:
            self.notebook_json=json.load(nbfile)

    def find_writefile_in_cells(self):
        """
        Find cells with `%%writefile` or `#%%writefile`  command at the start of a line in a notebook cell.

        This method parses cells in the loaded notebook and looks for the cell magic `%%writefile` or `#%%writefile`.
        If the cell includes this command, it extracts the file name, checks if the file is appended or overwritten, gets the cell
        content and type and stores this information in the cells_with_writefile dictionary.

        Raises:
            AttributeError: If this method is called before running the load_notebook method.

        Creates:
            self.cells_with_writefile (dict [str:dict]): A nested dictionary with the outer key being the cell number in the
              json source for the notebook and the inner keys being:
                -file(str): the file the `%%writefile` is pointing to
                - append_flag (bool): True if the found `%%writefile` has the `-a` append flag set in it
                - cell_type (str): the type of jupyter/ipython notebook cell the was parsed contiang the match to `%%writefile`
                - content (str): the content of the cell the was parsed contiang the match to `%%writefile`

            self._files_and_header_text (dict [str:str]; used for ext property getter/setter): a dictionary with the key being the unique file names found from the above matchs
                and the values being the header text to add and here will be an empty string
            self._files_and_paths (dict [str:Pathlib.Path]; used for ext property getter/setter): a dictionary key being the unique file names found from the above matchs
                and the values being set to `self.default_output_path` here

        Returns:
            None
        """
        if hasattr(self, 'notebook_json')==False:
            raise AttributeError('Need to run `self.load_notebook` to get `self.notebook_json` first')

        writefile_cmd_re_pattern=r'^\s*(#%%writefile)\s+(-a\s+)?(.*)'
        
        self.cells_with_writefile=dict()
        for i, nbcell in enumerate(self.notebook_json['cells']):
            
            cell_content='\n'.join([line.rstrip('\n') for line in nbcell['source']])
            
            matches=re.findall(writefile_cmd_re_pattern, cell_content, flags=re.MULTILINE)
            
            if len(matches)==1:
                _, append_flag, file= matches[0]
                if append_flag=='':
                    append_flag=False
                else:
                    append_flag=True
                
                # Remove all matches of the pattern in cell_content
                modified_cell_content = re.sub(writefile_cmd_re_pattern, '', cell_content, flags=re.MULTILINE)
                #TODO: need to remove any other cell magic commands or comment them out

                self.cells_with_writefile[i]={
                    'file':file, 
                    'append_flag':append_flag, 
                    'cell_type':nbcell['cell_type'], 
                    'content':modified_cell_content
                }
                
            if len(matches)>1:
                warnings.warn(f"In the notebook {self.notebook_path} in json entry for cell {i} more than one `%%writefile` was found at the beginning of a line in the cell's `source`"
                "Will only use the first found `%%writefile` line in the cell's content"
                )
            else:
                continue

        self.cells_with_writefile_check()
        self._files_and_header_text={k:'' for k in self.file_N_no_append_flags_count.keys()}
        self._files_and_paths={k:self.default_output_path for k in self.file_N_no_append_flags_count.keys() }
        #make the rpaths from source notebook to output
        self.files_rpaths_to_source_nb_maker()
        
     
    def cells_with_writefile_check(self):
        """
        Checks if attribute 'cells_with_writefile' exists and raises an
        AttributeError if not found. Further, it counts the quantity of cells
        without the append flag ('-a') for each file over the 'cells_with_writefile'
        dictionary.

        If the no append flag is not the lowest cell value for a specific file,
        it iterates over the 'file_N_no_append_flags_count' dictionary and raises
        a ValueError. A ValueError is raised again if there are more files without
        the '-a' flag than should be found once in a notebook.

        Modifies:
            Modifies class attribute:
                'file_N_no_append_flags_count': This attribute is a dictionary that
                holds character cells without the append flag against each file.

        Returns:
            None

        Raises:
            AttributeError: If the attribute 'cells_with_writefile' is not found.
            ValueError: If a file, that should have been found only once without
            the '-a' flag is either not found or found more than once.


        """
        if hasattr(self, 'cells_with_writefile')==False:
            raise AttributeError('Need to run `self.find_writefile_in_cells` first to get `self.cells_with_writefile`')

        self.file_N_no_append_flags_count={}
        
        for k, v in self.cells_with_writefile.items():
            if v['append_flag']==False:
                self.file_N_no_append_flags_count[v['file']]=self.file_N_no_append_flags_count.get(v['file'], 0)+1

            #TODO: add a check to make sure the no append flag is the lowest value cell for a given file
        
        for k,v in self.file_N_no_append_flags_count.items():
            if v==0:
                raise ValueError(f"`%%writefile {k}` without the `-a` to file {k} was not found at least once, where it should have occurred once and only once in notebook {self.notebook_path}")
            elif v>1:
                raise ValueError(f"`%%writefile {k}` without the `-a` to file {k} was found more than once, where it should have occurred once and only once in notebook {self.notebook_path}")

    @property
    def files_and_paths(self):
        """Returns the files and paths obtained by running `self.find_writefile_in_cells`.

        Note:
            This method raises an AttributeError if `self.find_writefile_in_cells` hasn't been run yet to get `self._files_and_paths`.

        Args:
            None

        Attributes modified:
            None

        Returns:
            self._files_and_paths (dict): The files and paths obtained by running `self.find_writefile_in_cells`. The dictionary contains file names as keys and corresponding file paths as values.

        Raises:
            AttributeError: If `self.find_writefile_in_cells` hasn't been run yet to get `self._files_and_paths`.
        """
        if hasattr(self, '_files_and_paths')==False:
            raise AttributeError('Need to run `self.find_writefile_in_cells` fist to get self._files_and_paths')
        else:
            return self._files_and_paths

    @files_and_paths.setter
    def files_and_paths(self, file_and_paths_dict):
        """Sets the files and paths for the software.

        This method validates and sets the '_files_and_paths' attribute with given dictionary.
        It also throws exceptions if preconditions are not met and triggers the creation of
        the relative paths from source notebook to output files.

        Args:
            file_and_paths_dict (dict): A dictionary containing the file names and corresponding paths.

        Raises:
            AttributeError: If `self.find_writefile_in_cells` has not been run first to get `self._files_and_paths`.
            ValueError: If `file_and_paths_dict` is not a dictionary.
            ValueError: If `file_and_paths_dict` does not have the same keys as `self._files_and_paths`.
            ValueError: If `file_and_paths_dict` contains non pathlib.Path object values for some keys.

        Attributes modified:
            self._files_and_paths (dict): Stores the updated file paths, dictionary key is filename and value is full path of that file.

        Note:
            This setter also calls the `self.output_path_check(v)` for each key-value pair in dictionary and `self.files_rpaths_to_source_nb_maker()` to remap the relative paths after setting the new values.
        """
        if hasattr(self, '_files_and_paths')==False:
            raise AttributeError('Need to run `self.find_writefile_in_cells` fist to get self._files_and_paths')
        if isinstance(file_and_paths_dict, dict)==False:
            raise ValueError('`file_and_paths_dict` must be a python dictionary ')
        if set(file_and_paths_dict.keys())!=set(self._files_and_paths.keys()):
            raise ValueError(f'`file_and_paths_dict` must have the keys: {self._files_and_paths.keys()}')

        non_path_values_keys=[k for k,v in file_and_paths_dict.items() if not isinstance(v, Path)]
        if non_path_values_keys:
            raise ValueError(f'`file_and_paths_dict` has non pathlib Path object values for the following keys: {non_path_values_keys}')

        file_and_paths_dict={k:self.output_path_check(v) for k,v in file_and_paths_dict.items()} 

        self._files_and_paths=file_and_paths_dict
        
        #remake the rpaths to the source notebook
        self.files_rpaths_to_source_nb_maker()

    def files_rpaths_to_source_nb_maker(self):
        """Sets the files and paths for the software.

        This method validates and sets the '_files_and_paths' attribute with given dictionary.
        It also throws exceptions if preconditions are not met and triggers the creation of
        the relative paths from source notebook to output files.

        Args:
            file_and_paths_dict (dict): A dictionary containing the file names and corresponding paths.

        Raises:
            AttributeError: If `self.find_writefile_in_cells` has not been run first to get `self._files_and_paths`.
            ValueError: If `file_and_paths_dict` is not a dictionary.
            ValueError: If `file_and_paths_dict` does not have the same keys as `self._files_and_paths`.
            ValueError: If `file_and_paths_dict` contains non pathlib.Path object values for some keys.

        Attributes modified:
            self._files_and_paths (dict): Stores the updated file paths, dictionary key is filename and value is full path of that file.

        Note:
            This setter also calls the `self.output_path_check(v)` for each key-value pair in dictionary and `self.files_rpaths_to_source_nb_maker()` to remap the relative paths after setting the new values.
        """
        if hasattr(self, '_files_and_paths')==False:
            raise AttributeError('Need to run `self.find_writefile_in_cells` fist to get self._files_and_paths')
        
        self.files_and_rpath_to_source_nb={k:Path(os.path.relpath(v, self.notebook_path))/self.notebook_path.name for k,v in self._files_and_paths.items()}


    @property
    def files_and_header_text(self):
        """Property to get the files and their corresponding header texts.

        This attribute is set within the `self.find_writefile_in_cells` method, so this
        property will raise an AttributeError if `self.find_writefile_in_cells` has not been run yet.

        Attributes read:
            _files_and_header_text (dict): A dictionary containing files as keys and header text as values.

        Returns:
            _files_and_header_text (dict): The dictionary of files and their header texts.

        Raises:
            AttributeError: If `self.find_writefile_in_cells` has not been run yet to set `self._files_and_header_text`.

        Note:
            To retrieve this attribute, `self.find_writefile_in_cells` must have been run first in order to set `self._files_and_header_text`.
        """
        if hasattr(self, '_files_and_header_text')==False:
            raise AttributeError('Need to run `self.find_writefile_in_cells` fist to get self._files_and_header_text')
        else:
            return self._files_and_header_text

    @files_and_header_text.setter
    def files_and_header_text(self, files_and_header_text_dict):
        """Assigns values to the `files_and_header_text` attribute.

        This method sets the `files_and_header_text` attribute of the class, which is a dictionary containing file names as keys and header text as values. It checks if the `find_writefile_in_cells` method has been run to populate `self._files_and_header_text`, and if not, an AttributeError is raised. Also, it validates that the input dictionary has similar keys with `self._files_and_header_text`.

        Args:
            files_and_header_text_dict (dict): A dictionary containing file names as keys and header text as values.

        Attributes created:
            None

        Attributes modified:
            self._files_and_header_text (dict): This attribute stores the dictionary representing the correlation between files and header text.

        Raises:
            AttributeError: If `self.find_writefile_in_cells` has not been run first to get `self._files_and_header_text`.
            ValueError: If `files_and_header_text_dict` is not a dictionary or does not have the same keys as `self._files_and_header_text`.
            ValueError: If `files_and_header_text_dict` contains non-string values for any of the keys.

        Returns:
            None
        """
        if hasattr(self, '_files_and_header_text')==False:
            raise AttributeError('Need to run `self.find_writefile_in_cells` fist to get self._files_and_header_text')
        if isinstance(files_and_header_text_dict, dict)==False:
            raise ValueError('`files_and_header_text_dict` must be a python dictionary ')
        if set(files_and_header_text_dict.keys())!=set(self._files_and_header_text.keys()):
            raise ValueError(f'`files_and_header_text_dict` must have the keys: {self._files_and_header_text.keys()}')

        non_str_values_keys=[k for k,v in files_and_header_text_dict.items() if not isinstance(v, str)]
        if non_str_values_keys:
            raise ValueError(f'`files_and_header_text_dict` has non string object values for the following keys: {non_str_values_keys}')

        self._files_and_header_text=files_and_header_text_dict
        
    
    def make_content_for_files(self, cell_types_to_write='all'):
        """Generates content for files based on specified cell types.

        This method creates `file_and_content`, a dictionary in which keys are the names of files
        and values are their respective content. Each file's content is built based on the types of cells
        of the source notebook file and the given `cell_types_to_write` option.

        It first checks if the `_files_and_paths` attribute has been set by the
        `self.find_writefile_in_cells` method. If not, it raises an `AttributeError`.

        Among the valid options for `cell_types_to_write` are 'all', 'code', 'code_and_markdown', 'markdown',
        'code_raw', 'raw', 'markdown_raw'. If an invalid option is given, it raises a `ValueError`.

        Note:
            This method creates and modifies the `file_and_content` attribute. This attribute is a dictionary
            where each key-value pair represents a file name and its corresponding content.

        Args:
            cell_types_to_write (:obj:`str`, optional; default: 'all'): The types of cells to include in
                the generated content. The default is 'all', which includes all types of cells. The other
                valid values are: 'code', 'code_and_markdown', 'markdown', 'code_raw', 'raw', 'markdown_raw'.

        Attributes created:
            self.file_and_content (dict): A dictionary in which keys are the names of the files and values
                are their corresponding content.

        Attributes modified:
            None

        Returns:
            None

        Raises:
            AttributeError: Raises error if `self.find_writefile_in_cells` not run first.
            ValueError: Raises error if `cell_types_to_write` is not a known input.
        """
        if hasattr(self, '_files_and_paths')==False:
            raise AttributeError('Need to run `self.find_writefile_in_cells` fist to get self._files_and_paths')
        
        cell_types_to_write=cell_types_to_write.lower()
        
        valid_cell_types_to_write_args=['all', 'code', 'code_and_markdown', 'markdown', 'code_raw', 'raw', 'markdown_raw']
        if cell_types_to_write not in valid_cell_types_to_write_args:
            raise ValueError(f"{cell_types_to_write =} is a unknown input, where instead it must be one of {valid_cell_types_to_write_args}")

        self.file_and_content=dict()
        for file, path in self._files_and_paths.items():
            #add the extraction source
            self.file_and_content[file]=self.file_and_content.get(file, f"#Exstracted from source notebook with relative path this files initial creation: {self.files_and_rpath_to_source_nb[file]}\n")
            #add the header
            self.file_and_content[file]=self.file_and_content.get(file, '\n'.join([f"#{line}" for line in self._files_and_header_text[file].splitlines()]))
            
            for cell_number, cell_info in self.cells_with_writefile.items():
                if cell_info['file']!=file:
                    continue
                match cell_info['cell_type']:
                    case "code":
                        if cell_types_to_write in ['all', 'code', 'code_and_markdown', 'code_raw']:
                            self.file_and_content[file]+=('\n'+cell_info['content']+'\n')
                            
                    case 'markdown':
                        if cell_types_to_write in ['all', 'code_and_markdown', 'markdown', 'markdown_raw']:
                            self.file_and_content[file]+=('\n\n########\n'+'\n'.join([f"#{line}" for line in cell_info['content'].splitlines()])+'\n########\n')
                            
                    case 'raw':
                        if cell_types_to_write in ['all', 'code_raw', 'raw', 'markdown_raw']:
                            self.file_and_content[file]+=('\n'+cell_info['content']+'\n')

    def write_to_files(self, cell_types_to_write='all'):
        """
        Find cells with `%%writefile` or `#%%writefile` command at the start of a line in a notebook cell.

        This method finds the cells with `%%writefile` or `#%%writefile`, extracts the file name, cell type and its content,
        and stores this information in the cells_with_writefile dictionary.

        Raises:
            AttributeError: If this method is called before running the load_notebook method.

        Note:
            This method creates the attribute self.cells_with_writefile.

        Returns:
            None
        """
        if hasattr(self, 'file_and_content')==False:
            self.make_content_for_files(cell_types_to_write=cell_types_to_write)

        for file, content in self.file_and_content.items():
            file_path=self._files_and_paths[file]/file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            
