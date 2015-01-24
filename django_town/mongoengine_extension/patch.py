# from mongoengine.base.metaclasses import MetaDict
#
#
# def merge_patch(self, new_options):
# for k, v in new_options.iteritems():
#         if k in self._merge_options:
#             from_ = self.get(k, [])
#             if isinstance(from_, list) and isinstance(v, dict) and len(from_) == 0:
#                 self[k] = v
#             else:
#                 self[k] = self.get(k, []) + v
#         else:
#             self[k] = v
#
#
# setattr(MetaDict, 'merge', merge_patch)