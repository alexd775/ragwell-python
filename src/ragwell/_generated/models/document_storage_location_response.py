from __future__ import annotations

from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.document_storage_location_response_geographic_guarantee import (
    DocumentStorageLocationResponseGeographicGuarantee,
)
from ..models.document_storage_location_response_jurisdiction_type_0 import (
    DocumentStorageLocationResponseJurisdictionType0,
)
from ..models.document_storage_location_response_provider import (
    DocumentStorageLocationResponseProvider,
)
from ..models.document_storage_location_response_selection_status import (
    DocumentStorageLocationResponseSelectionStatus,
)

T = TypeVar("T", bound="DocumentStorageLocationResponse")


@_attrs_define
class DocumentStorageLocationResponse:
    geographic_guarantee: DocumentStorageLocationResponseGeographicGuarantee
    jurisdiction: DocumentStorageLocationResponseJurisdictionType0 | None
    location_name: str
    management: Literal["ragwell_managed"]
    provider: DocumentStorageLocationResponseProvider
    provider_name: str
    selection_status: DocumentStorageLocationResponseSelectionStatus
    zone_id: str
    zone_name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        geographic_guarantee = self.geographic_guarantee.value

        jurisdiction: None | str
        if isinstance(
            self.jurisdiction, DocumentStorageLocationResponseJurisdictionType0
        ):
            jurisdiction = self.jurisdiction.value
        else:
            jurisdiction = self.jurisdiction

        location_name = self.location_name

        management = self.management

        provider = self.provider.value

        provider_name = self.provider_name

        selection_status = self.selection_status.value

        zone_id = self.zone_id

        zone_name = self.zone_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "geographic_guarantee": geographic_guarantee,
                "jurisdiction": jurisdiction,
                "location_name": location_name,
                "management": management,
                "provider": provider,
                "provider_name": provider_name,
                "selection_status": selection_status,
                "zone_id": zone_id,
                "zone_name": zone_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        geographic_guarantee = DocumentStorageLocationResponseGeographicGuarantee(
            d.pop("geographic_guarantee")
        )

        def _parse_jurisdiction(
            data: object,
        ) -> DocumentStorageLocationResponseJurisdictionType0 | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                jurisdiction_type_0 = DocumentStorageLocationResponseJurisdictionType0(
                    data
                )

                return jurisdiction_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DocumentStorageLocationResponseJurisdictionType0 | None, data)

        jurisdiction = _parse_jurisdiction(d.pop("jurisdiction"))

        location_name = d.pop("location_name")

        management = cast(Literal["ragwell_managed"], d.pop("management"))
        if management != "ragwell_managed":
            raise ValueError(
                f"management must match const 'ragwell_managed', got '{management}'"
            )

        provider = DocumentStorageLocationResponseProvider(d.pop("provider"))

        provider_name = d.pop("provider_name")

        selection_status = DocumentStorageLocationResponseSelectionStatus(
            d.pop("selection_status")
        )

        zone_id = d.pop("zone_id")

        zone_name = d.pop("zone_name")

        document_storage_location_response = cls(
            geographic_guarantee=geographic_guarantee,
            jurisdiction=jurisdiction,
            location_name=location_name,
            management=management,
            provider=provider,
            provider_name=provider_name,
            selection_status=selection_status,
            zone_id=zone_id,
            zone_name=zone_name,
        )

        document_storage_location_response.additional_properties = d
        return document_storage_location_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
