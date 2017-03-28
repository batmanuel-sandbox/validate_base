# See COPYRIGHT file at the top of the source tree.
"""Tools for building and parsing fully-qualified names of metrics and
specifications.
"""
from __future__ import print_function

__all__ = ['Name']


class Name(object):
    """Semantic name of a package, `lsst.validate.base.Metric` or
    `lsst.validate.base.Specification` in the `lsst.validate` framework.

    ``Name``\ s are immutable.

    Parameters
    ----------
    package : `str` or `Name`
       Name of the package, either as a string (``'validate_drp'``,
       for example) or as a Name object (``Name(package='validate_drp')``
       for example).

       The ``package`` field can also be fully specified::

           Name(package='validate_drp.PA1.design_gri')

       or used as the sole positional argument::

           Name('validate_drp.PA1.design_gri')
    metric : `str` or `Name`
       Name of the metric. The name can be relative (``'PA'``) or
       fully-specified (``'validate_drp.PA1'``).
    spec : `str` or `Name`
       Name of the specification. The name can be bare (``'design_gri'``),
       metric-relative (``'PA1.design_gri'``) or fully-specified
       (``'validate_drp.PA1.design_gri'``)

    Raises
    ------
    TypeError
       Raised when arguments cannot be parsed or conflict (for example, if two
       different package names are specified through two different fields).
    """

    def __init__(self, package=None, metric=None, spec=None):
        self._package = None
        self._metric = None
        self._spec = None

        if package is not None:
            if isinstance(package, Name):
                self._package = package.package
                self._metric = package.metric
                self._spec = package.spec
            else:
                # Assume a string type
                try:
                    self._package, self._metric, self._spec = \
                        Name._parse_fqn_string(package)
                except ValueError as e:
                    # Want to raise TypeError in __init__
                    raise TypeError(str(e))

        if metric is not None:
            if isinstance(metric, Name):
                if metric.has_metric is False:
                    raise TypeError(
                        'metric={metric!r} argument does not include metric '
                        'information.'.format(metric=metric))
                _package = metric.package
                _metric = metric.metric
                _spec = metric.spec
            else:
                try:
                    _package, _metric = \
                        Name._parse_metric_name_string(metric)
                    _spec = None
                except ValueError as e:
                    # Want to raise TypeError in __init__
                    raise TypeError(str(e))

            # Ensure none of the new information is inconsistent
            self._init_new_package_info(_package)
            self._init_new_metric_info(_metric)
            self._init_new_spec_info(_spec)

        if spec is not None:
            if isinstance(spec, Name):
                if spec.has_spec is False:
                    raise TypeError(
                        'spec={spec!r} argument does not include '
                        'specification information'.format(spec=spec))
                _package = spec.package
                _metric = spec.metric
                _spec = spec.spec
            else:
                try:
                    _package, _metric, _spec = \
                        Name._parse_spec_name_string(spec)
                except ValueError as e:
                    # want to raise TypeError in __init__
                    raise TypeError(str(e))

            # Ensure none of the new information is inconsistent
            self._init_new_package_info(_package)
            self._init_new_metric_info(_metric)
            self._init_new_spec_info(_spec)

        # Ensure the name doesn't have a metric gap
        if self._package is not None \
                and self._spec is not None \
                and self._metric is None:
            raise TypeError("Missing 'metric' given package={package!r} "
                            "spec={spec!r}".format(package=package,
                                                   spec=spec))

    def _init_new_package_info(self, package):
        """Check and add new package information (for __init__)."""
        if package is not None:
            if self._package is None or package == self._package:
                # There's new or consistent package info
                self._package = package
            else:
                message = 'You provided a conflicting package={package!r}.'
                raise TypeError(message.format(package=package))

    def _init_new_metric_info(self, metric):
        """Check and add new metric information (for __init__)."""
        if metric is not None:
            if self._metric is None or metric == self._metric:
                # There's new or consistent metric info
                self._metric = metric
            else:
                message = 'You provided a conflicting metric={metric!r}.'
                raise TypeError(message.format(metric=metric))

    def _init_new_spec_info(self, spec):
        """Check and add new spec information (for __init__)."""
        if spec is not None:
            if self._spec is None or spec == self._spec:
                # There's new or consistent spec info
                self._spec = spec
            else:
                message = 'You provided a conflicting spec={spec!r}.'
                raise TypeError(message.format(spec=spec))

    @staticmethod
    def _parse_fqn_string(fqn):
        """Parse a fully-qualified name.
        """
        parts = fqn.split('.')
        if len(parts) == 1:
            # Must be a package name alone
            return parts[0], None, None
        if len(parts) == 2:
            # Must be a fully-qualified metric name
            return parts[0], parts[1], None
        elif len(parts) == 3:
            # Must be a fully-qualified specification name
            return parts
        else:
            # Don't know what this string is
            raise ValueError('Cannot parse fully qualified name: '
                             '{0!r}'.format(fqn))

    @staticmethod
    def _parse_metric_name_string(name):
        """Parse a metric name."""
        parts = name.split('.')
        if len(parts) == 2:
            # Must be a fully-qualified metric name
            return parts[0], parts[1]
        elif len(parts) == 1:
            # A bare metric name
            return None, parts[0]
        else:
            # Don't know what this string is
            raise ValueError('Cannot parse metric name: '
                             '{0!r}'.format(name))

    @staticmethod
    def _parse_spec_name_string(name):
        """Parse a specification name."""
        parts = name.split('.')
        if len(parts) == 1:
            # Bare specification name
            return None, None, parts[0]
        elif len(parts) == 2:
            # metric-relative specification name
            return None, parts[0], parts[1]
        elif len(parts) == 3:
            # fully-qualified specification name
            return parts
        else:
            # Don't know what this string is
            raise ValueError('Cannot parse specification name: '
                             '{0!r}'.format(name))

    @property
    def package(self):
        """Package name (`str`)."""
        return self._package

    @property
    def metric(self):
        """Metric name (`str`)."""
        return self._metric

    @property
    def spec(self):
        """Specification name (`str`)."""
        return self._spec

    def __eq__(self, other):
        return (self.package == other.package) and \
            (self.metric == other.metric) and \
            (self.spec == other.spec)

    def __hash__(self):
        return hash((self.package, self.metric, self.spec))

    def __contains__(self, name):
        """Test if another Name is contained by this Name."""
        contains = True  # tests will disprove membership

        if self.is_package:
            if name.is_package:
                contains = False
            else:
                contains = self.package == name.package

        elif self.is_metric:
            if name.is_metric:
                contains = False
            else:
                if self.has_package or name.has_package:
                    contains = contains and (self.package == name.package)

                contains = contains and (self.metric == name.metric)

        else:
            # Must be a specification, which cannot 'contain' anything
            contains = False

        return contains

    @property
    def has_package(self):
        """`True` if this object contains a package name (`bool`)."""
        if self.package is not None:
            return True
        else:
            return False

    @property
    def has_spec(self):
        """`True` if this object contains a specification name, either
        relative or fully-qualified (`bool`).
        """
        if self.spec is not None:
            return True
        else:
            return False

    @property
    def has_metric(self):
        """`True` if this object contains a metric name, either
        relative or fully-qualified (`bool`).
        """
        if self.metric is not None:
            return True
        else:
            return False

    @property
    def has_relative(self):
        """`True` if a relative specification name can be formed from this
        object, i.e., `metric` and `spec` attributes are set (`bool`).
        """
        if self.is_spec and self.has_metric:
            return True
        else:
            return False

    @property
    def is_package(self):
        """`True` if this object is a package name (`bool`)."""
        if self.has_package and \
                self.is_metric is False and \
                self.is_spec is False:
            return True
        else:
            return False

    @property
    def is_metric(self):
        """`True` if this object is a metric name, either relative or
        fully-qualified (`bool`).
        """
        if self.has_metric is True and self.has_spec is False:
            return True
        else:
            return False

    @property
    def is_spec(self):
        """`True` if this object is a specification name, either relative or
        fully-qualified (`bool`).
        """
        if self.has_spec is True:
            return True
        else:
            return False

    @property
    def is_fq(self):
        """`True` if this object is a fully-qualified name of either a
        package, metric or specification (`bool`).

        Examples:

        - ``'validate_drp'`` is a fully-qualified package name.
        - ``'validate_drp.PA1'`` is a fully-qualified metric name.
        - ``'validate_drp.PA1.design_gri'`` is a fully-qualified specification
          name.
        """
        if self.is_package:
            # package names are by definition fully qualified
            return True
        elif self.is_metric and self.has_package:
            # fully-qualified metric
            return True
        elif self.is_spec and self.has_package and self.has_metric:
            # fully-qualified specification
            return True
        else:
            return False

    @property
    def is_relative(self):
        """`True` if this object is a specification name that's not
        fully-qualified, but is relative to a metric name (`bool`).
        relative to a base name. (`bool`).

        For example, ``PA1.design_gri`` is a relative specification name.

        Package and metric names are never relative.
        """
        if self.is_spec and \
                self.has_metric is True and \
                self.has_package is False:
            return True
        else:
            return False

    def __repr__(self):
        if self.is_package:
            return 'Name({self.package!r})'.format(self=self)
        elif self.is_metric and not self.is_fq:
            return 'Name(metric={self.metric!r})'.format(self=self)
        elif self.is_metric and self.is_fq:
            return 'Name({self.package!r}, {self.metric!r})'.format(
                self=self)
        elif self.is_spec and not self.is_fq and not self.is_relative:
            return 'Name(spec={self.spec!r})'.format(
                self=self)
        elif self.is_spec and not self.is_fq and self.is_relative:
            return 'Name(metric={self.metric!r}, spec={self.spec!r})'.format(
                self=self)
        else:
            # Should be a fully-qualified specification
            template = 'Name({self.package!r}, {self.metric!r}, {self.spec!r})'
            return template.format(self=self)

    def __str__(self):
        if self.is_package:
            return self.package
        elif self.is_metric and not self.is_fq:
            return self.metric
        elif self.is_metric and self.is_fq:
            return '{self.package}.{self.metric}'.format(self=self)
        elif self.is_spec and not self.is_fq and not self.is_relative:
            return self.spec
        elif self.is_spec and not self.is_fq and self.is_relative:
            return '{self.metric}.{self.spec}'.format(self=self)
        else:
            # Should be a fully-qualified specification
            return '{self.package}.{self.metric}.{self.spec}'.format(
                self=self)

    @property
    def fqn(self):
        """The fully-qualified name (`str`).

        Raises
        ------
        AttributeError
           If the name is not a fully-qualified name (check `is_fq`)
        """
        if self.is_fq:
            return str(self)
        else:
            message = '{self!r} is not a fully-qualified name'
            raise AttributeError(message.format(self=self))

    @property
    def relative_name(self):
        """The relative specification name (`str`).

        Raises
        ------
        AttributeError
           If the object does not represent a specification, or if a relative
           name cannot be formed because the `metric` is None.
        """
        if self.has_relative:
            return '{self.metric}.{self.spec}'.format(self=self)
        else:
            message = '{self!r} is not a relative specification name'
            raise AttributeError(message.format(self=self))