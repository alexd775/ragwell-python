from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.embedding_connection_response_funding_source import (
    EmbeddingConnectionResponseFundingSource,
)
from ..models.embedding_connection_response_health import (
    EmbeddingConnectionResponseHealth,
)
from ..models.embedding_connection_response_status import (
    EmbeddingConnectionResponseStatus,
)

if TYPE_CHECKING:
    from ..models.embedding_connection_notice_response import (
        EmbeddingConnectionNoticeResponse,
    )


T = TypeVar("T", bound="EmbeddingConnectionResponse")


@_attrs_define
class EmbeddingConnectionResponse:
    customer_key_configured: bool
    endpoint_url: str
    funding_source: EmbeddingConnectionResponseFundingSource
    health: EmbeddingConnectionResponseHealth
    health_code: None | str
    model: str
    notices: list[EmbeddingConnectionNoticeResponse]
    provider: str
    revision: int
    status: EmbeddingConnectionResponseStatus
    system_credentials_available: bool
    updated_at: datetime.datetime
    validated_at: datetime.datetime | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        customer_key_configured = self.customer_key_configured

        endpoint_url = self.endpoint_url

        funding_source = self.funding_source.value

        health = self.health.value

        health_code: None | str
        health_code = self.health_code

        model = self.model

        notices = []
        for notices_item_data in self.notices:
            notices_item = notices_item_data.to_dict()
            notices.append(notices_item)

        provider = self.provider

        revision = self.revision

        status = self.status.value

        system_credentials_available = self.system_credentials_available

        updated_at = self.updated_at.isoformat()

        validated_at: None | str
        if isinstance(self.validated_at, datetime.datetime):
            validated_at = self.validated_at.isoformat()
        else:
            validated_at = self.validated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "customer_key_configured": customer_key_configured,
                "endpoint_url": endpoint_url,
                "funding_source": funding_source,
                "health": health,
                "health_code": health_code,
                "model": model,
                "notices": notices,
                "provider": provider,
                "revision": revision,
                "status": status,
                "system_credentials_available": system_credentials_available,
                "updated_at": updated_at,
                "validated_at": validated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.embedding_connection_notice_response import (
            EmbeddingConnectionNoticeResponse,
        )

        d = dict(src_dict)
        customer_key_configured = d.pop("customer_key_configured")

        endpoint_url = d.pop("endpoint_url")

        funding_source = EmbeddingConnectionResponseFundingSource(
            d.pop("funding_source")
        )

        health = EmbeddingConnectionResponseHealth(d.pop("health"))

        def _parse_health_code(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        health_code = _parse_health_code(d.pop("health_code"))

        model = d.pop("model")

        notices = []
        _notices = d.pop("notices")
        for notices_item_data in _notices:
            notices_item = EmbeddingConnectionNoticeResponse.from_dict(
                notices_item_data
            )

            notices.append(notices_item)

        provider = d.pop("provider")

        revision = d.pop("revision")

        status = EmbeddingConnectionResponseStatus(d.pop("status"))

        system_credentials_available = d.pop("system_credentials_available")

        updated_at = datetime.datetime.fromisoformat(d.pop("updated_at"))

        def _parse_validated_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                validated_at_type_0 = datetime.datetime.fromisoformat(data)

                return validated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        validated_at = _parse_validated_at(d.pop("validated_at"))

        embedding_connection_response = cls(
            customer_key_configured=customer_key_configured,
            endpoint_url=endpoint_url,
            funding_source=funding_source,
            health=health,
            health_code=health_code,
            model=model,
            notices=notices,
            provider=provider,
            revision=revision,
            status=status,
            system_credentials_available=system_credentials_available,
            updated_at=updated_at,
            validated_at=validated_at,
        )

        embedding_connection_response.additional_properties = d
        return embedding_connection_response

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
