
Mapped SDK API
===============

.. toctree::
   :maxdepth: 2
   :caption: Contents:


Request and Config Class
--------------------------
.. py:currentmodule:: aliyun.log
.. autosummary::
   GetHistogramsRequest
   GetLogsRequest
   GetProjectLogsRequest
   ListTopicsRequest
   ListLogstoresRequest
   PutLogsRequest
   LogtailConfigGenerator
   SeperatorFileConfigDetail
   SimpleFileConfigDetail
   FullRegFileConfigDetail
   JsonFileConfigDetail
   ApsaraFileConfigDetail
   SyslogConfigDetail
   MachineGroupDetail
   IndexConfig
   OssShipperConfig
   OdpsShipperConfig
   ShipperTask


Project
--------
.. py:currentmodule:: aliyun.log.LogClient
.. autosummary::
   list_project
   create_project
   get_project
   delete_project
   copy_project


Logstore
----------
.. autosummary::
   list_logstore
   create_logstore
   get_logstore
   update_logstore
   delete_logstore
   list_topics


Index
-------
.. autosummary::
   create_index
   update_index
   delete_index
   get_index_config


Logtail Config
-----------------
.. autosummary::
   create_logtail_config
   update_logtail_config
   delete_logtail_config
   get_logtail_config
   list_logtail_config


Machine Group
---------------
.. autosummary::
   create_machine_group
   delete_machine_group
   update_machine_group
   get_machine_group
   list_machine_group
   list_machines


Apply Logtail Config
----------------------
.. autosummary::
   apply_config_to_machine_group
   remove_config_to_machine_group
   get_machine_group_applied_configs
   get_config_applied_machine_groups


Shard
-------
.. autosummary::
   list_shards
   split_shard
   merge_shard


Cursor
--------
.. autosummary::
   get_cursor
   get_cursor_time
   get_previous_cursor_time
   get_begin_cursor
   get_end_cursor


Logs
--------
.. autosummary::
   put_logs
   pull_logs
   pull_log
   get_log
   get_logs
   get_log_all
   get_histograms
   get_project_logs

Consumer group
----------------
.. autosummary::
   create_consumer_group
   update_consumer_group
   delete_consumer_group
   list_consumer_group
   update_check_point
   get_check_point


Shipper
----------
.. autosummary::
   create_shipper
   update_shipper
   delete_shipper
   get_shipper_config
   list_shipper
   get_shipper_tasks
   retry_shipper_tasks


Definitions
-------------

.. autoclass:: aliyun.log.LogClient
   :members:
.. py:currentmodule:: aliyun.log
.. autoclass:: LogException
.. autoclass:: GetHistogramsRequest
.. autoclass:: GetLogsRequest
.. autoclass:: GetProjectLogsRequest
.. autoclass:: IndexConfig
.. autoclass:: ListTopicsRequest
.. autoclass:: ListLogstoresRequest
.. autoclass:: LogtailConfigGenerator
   :members:
.. autoclass:: SeperatorFileConfigDetail
.. autoclass:: SimpleFileConfigDetail
.. autoclass:: FullRegFileConfigDetail
.. autoclass:: JsonFileConfigDetail
.. autoclass:: ApsaraFileConfigDetail
.. autoclass:: SyslogConfigDetail
.. autoclass:: MachineGroupDetail
.. autoclass:: PutLogsRequest
.. autoclass:: OssShipperConfig
.. autoclass:: OdpsShipperConfig
.. autoclass:: ShipperTask
