# **Data dictionary**

#  [**JSON**](https://data.opensanctions.org/meta/model.json)

In this reference you'll find detailed explanations of the data model used by OpenSanctions, including the used entity types and their respective properties.

## **Entities**

OpenSanctions collects data about real-world [entities](https://www.opensanctions.org/docs/entities/), such as people, companies, sanctions and addresses, but also the relationships between them. In order to process that data, it is internally converted into an object graph that is defined below. Different exporters then might simplify the data for end-users.

The data model used by OpenSanctions is [FollowTheMoney](https://followthemoney.tech/), an ontology used in anti-corruption data analysis \- in particular by the [OpenAleph data platform](https://openaleph.org/). Only a subset of the entity types defined in FtM are used by OpenSanctions.

Developer note: All of the information detailed below is also available in the [JSON model file](https://data.opensanctions.org/meta/model.json) for OpenSanctions. FollowTheMoney additionally provides libraries for [Python](https://pypi.org/project/followthemoney/), [Java](https://central.sonatype.com/artifact/tech.followthemoney/followthemoney) and [TypeScript](https://www.npmjs.com/package/@opensanctions/followthemoney) that can be used to process and analyse entities more easily.

## **Schema types**

All entities in OpenSanctions must conform to a schema, a definition that states what properties they are allowed to have. Some properties also allow entities to reference other entities, turning the entities into a graph. [Read more about the entity graph...](https://www.opensanctions.org/docs/entities/)

The following schema types are currently referenced in OpenSanctions:

* [Address](https://www.opensanctions.org/reference/#schema.Address)  
* [Airplane](https://www.opensanctions.org/reference/#schema.Airplane)  
* [Asset](https://www.opensanctions.org/reference/#schema.Asset)  
* [Associate](https://www.opensanctions.org/reference/#schema.Associate)  
* [Company](https://www.opensanctions.org/reference/#schema.Company)  
* [CryptoWallet](https://www.opensanctions.org/reference/#schema.CryptoWallet)  
* [Debt](https://www.opensanctions.org/reference/#schema.Debt)  
* [Directorship](https://www.opensanctions.org/reference/#schema.Directorship)  
* [Employment](https://www.opensanctions.org/reference/#schema.Employment)  
* [Family](https://www.opensanctions.org/reference/#schema.Family)  
* [Identification](https://www.opensanctions.org/reference/#schema.Identification)  
* [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity)  
* [Membership](https://www.opensanctions.org/reference/#schema.Membership)  
* [Occupancy](https://www.opensanctions.org/reference/#schema.Occupancy)  
* [Organization](https://www.opensanctions.org/reference/#schema.Organization)  
* [Ownership](https://www.opensanctions.org/reference/#schema.Ownership)  
* [Passport](https://www.opensanctions.org/reference/#schema.Passport)  
* [Payment](https://www.opensanctions.org/reference/#schema.Payment)  
* [Person](https://www.opensanctions.org/reference/#schema.Person)  
* [Position](https://www.opensanctions.org/reference/#schema.Position)  
* [PublicBody](https://www.opensanctions.org/reference/#schema.PublicBody)  
* [Representation](https://www.opensanctions.org/reference/#schema.Representation)  
* [Sanction](https://www.opensanctions.org/reference/#schema.Sanction)  
* [Security](https://www.opensanctions.org/reference/#schema.Security)  
* [Succession](https://www.opensanctions.org/reference/#schema.Succession)  
* [UnknownLink](https://www.opensanctions.org/reference/#schema.UnknownLink)  
* [Vessel](https://www.opensanctions.org/reference/#schema.Vessel)

## **Schema definitions in detail**

### **Address \- Addresses**

A location associated with an entity.

| Extends | [Thing](https://www.opensanctions.org/reference/#schema.Thing) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Thing:name | name | 384 | Name |  |
| Thing:summary | text | 65000 | Summary |  |
| Thing:description | text | 65000 | Description |  |
| Address:country | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country |  |
| Thing:alias | name | 384 | Other name |  |
| Thing:previousName | name | 384 | Previous name |  |
| Thing:weakAlias | name | 384 | Weak alias |  |
| Thing:sourceUrl | url | 4096 | Source link |  |
| Thing:publisher | string | 1024 | Publishing source |  |
| Thing:wikidataId | identifier | 32 | Wikidata ID | format: qid |
| Thing:keywords | string | 1024 | Keywords |  |
| Thing:topics | [topic](https://www.opensanctions.org/reference/#type.topic) | 64 | Topics |  |
| Thing:address | address | 250 | Address |  |
| Thing:addressEntity | [Address](https://www.opensanctions.org/reference/#schema.Address) | 200 | Address | see [Address:things](https://www.opensanctions.org/reference/#prop.Address:things) (inverse) |
| Thing:program | string | 1024 | Program | Regulatory program or sanctions list on which an entity is listed. |
| Thing:notes | text | 65000 | Notes |  |
| Thing:createdAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Created at |  |
| Thing:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Address:full | address | 250 | Full address |  |
| Address:remarks | string | 1024 | Remarks | Handling instructions, like 'care of'. |
| Address:postOfficeBox | string | 1024 | PO Box | A mailbox identifier at the post office |
| Address:street | string | 1024 | Street address |  |
| Address:city | string | 1024 | City | City, town, village or other locality |
| Address:postalCode | string | 16 | Postal code | Zip code or postcode. |
| Address:region | string | 1024 | Region | Also province or area. |
| Address:state | string | 1024 | State | State or federal unit. |

### **Airplane \- Airplanes**

An airplane, helicopter or other flying vehicle.

| Extends | [Vehicle](https://www.opensanctions.org/reference/#schema.Vehicle) · [Asset](https://www.opensanctions.org/reference/#schema.Asset) · [Thing](https://www.opensanctions.org/reference/#schema.Thing) · [Value](https://www.opensanctions.org/reference/#schema.Value) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Thing:name | name | 384 | Name |  |
| Thing:summary | text | 65000 | Summary |  |
| Thing:description | text | 65000 | Description |  |
| Thing:country | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country |  |
| Thing:alias | name | 384 | Other name |  |
| Thing:previousName | name | 384 | Previous name |  |
| Thing:weakAlias | name | 384 | Weak alias |  |
| Thing:sourceUrl | url | 4096 | Source link |  |
| Thing:publisher | string | 1024 | Publishing source |  |
| Thing:wikidataId | identifier | 32 | Wikidata ID | format: qid |
| Thing:keywords | string | 1024 | Keywords |  |
| Thing:topics | [topic](https://www.opensanctions.org/reference/#type.topic) | 64 | Topics |  |
| Thing:address | address | 250 | Address |  |
| Thing:addressEntity | [Address](https://www.opensanctions.org/reference/#schema.Address) | 200 | Address | see [Address:things](https://www.opensanctions.org/reference/#prop.Address:things) (inverse) |
| Thing:program | string | 1024 | Program | Regulatory program or sanctions list on which an entity is listed. |
| Thing:notes | text | 65000 | Notes |  |
| Thing:createdAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Created at |  |
| Thing:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Value:amount | number | 250 | Amount |  |
| Value:currency | string | 1024 | Currency |  |
| Value:amountUsd | number | 250 | Amount in USD |  |
| Vehicle:registrationNumber | identifier | 64 | Registration number |  |
| Vehicle:type | string | 1024 | Type |  |
| Vehicle:model | string | 1024 | Model |  |
| Vehicle:owner | [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) | 200 | Owner | see [LegalEntity:ownedVehicles](https://www.opensanctions.org/reference/#prop.LegalEntity:ownedVehicles) (inverse) |
| Vehicle:buildDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Build Date |  |
| Airplane:serialNumber | identifier | 64 | Serial Number |  |

### **Asset \- Assets**

A piece of property which can be owned and assigned a monetary value.

| Extends | [Thing](https://www.opensanctions.org/reference/#schema.Thing) · [Value](https://www.opensanctions.org/reference/#schema.Value) |
| :---: | :---- |
| **Sub-types** | [Airplane](https://www.opensanctions.org/reference/#schema.Airplane) · [Security](https://www.opensanctions.org/reference/#schema.Security) · [Vehicle](https://www.opensanctions.org/reference/#schema.Vehicle) · [Vessel](https://www.opensanctions.org/reference/#schema.Vessel) · [Company](https://www.opensanctions.org/reference/#schema.Company) |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Thing:name | name | 384 | Name |  |
| Thing:summary | text | 65000 | Summary |  |
| Thing:description | text | 65000 | Description |  |
| Thing:country | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country |  |
| Thing:alias | name | 384 | Other name |  |
| Thing:previousName | name | 384 | Previous name |  |
| Thing:weakAlias | name | 384 | Weak alias |  |
| Thing:sourceUrl | url | 4096 | Source link |  |
| Thing:publisher | string | 1024 | Publishing source |  |
| Thing:wikidataId | identifier | 32 | Wikidata ID | format: qid |
| Thing:keywords | string | 1024 | Keywords |  |
| Thing:topics | [topic](https://www.opensanctions.org/reference/#type.topic) | 64 | Topics |  |
| Thing:address | address | 250 | Address |  |
| Thing:addressEntity | [Address](https://www.opensanctions.org/reference/#schema.Address) | 200 | Address | see [Address:things](https://www.opensanctions.org/reference/#prop.Address:things) (inverse) |
| Thing:program | string | 1024 | Program | Regulatory program or sanctions list on which an entity is listed. |
| Thing:notes | text | 65000 | Notes |  |
| Thing:createdAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Created at |  |
| Thing:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Value:amount | number | 250 | Amount |  |
| Value:currency | string | 1024 | Currency |  |
| Value:amountUsd | number | 250 | Amount in USD |  |

### **Associate \- Associates**

Non-family association between two people

| Extends | [Interval](https://www.opensanctions.org/reference/#schema.Interval) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Interval:startDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Start date |  |
| Interval:endDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | End date |  |
| Interval:date | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Date |  |
| Interval:summary | text | 65000 | Summary |  |
| Interval:description | text | 65000 | Description |  |
| Interval:recordId | string | 1024 | Record ID |  |
| Interval:sourceUrl | url | 4096 | Source link |  |
| Interval:publisher | string | 1024 | Publishing source |  |
| Interval:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Associate:person | [Person](https://www.opensanctions.org/reference/#schema.Person) | 200 | Person | see [Person:associates](https://www.opensanctions.org/reference/#prop.Person:associates) (inverse)The subject of the association. |
| Associate:associate | [Person](https://www.opensanctions.org/reference/#schema.Person) | 200 | Associate | see [Person:associations](https://www.opensanctions.org/reference/#prop.Person:associations) (inverse)An associate of the subject person. |
| Associate:relationship | string | 1024 | Relationship | Nature of the association |

### **Company \- Companies**

A corporation, usually for profit. Does not distinguish between private and public companies, and can also be used to model more specific constructs like trusts and funds. Companies are assets, so they can be owned by other legal entities.

| Extends | [Asset](https://www.opensanctions.org/reference/#schema.Asset) · [Thing](https://www.opensanctions.org/reference/#schema.Thing) · [Value](https://www.opensanctions.org/reference/#schema.Value) · [Organization](https://www.opensanctions.org/reference/#schema.Organization) · [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Thing:name | name | 384 | Name |  |
| Thing:summary | text | 65000 | Summary |  |
| Thing:description | text | 65000 | Description |  |
| Thing:country | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country |  |
| Thing:alias | name | 384 | Other name |  |
| Thing:previousName | name | 384 | Previous name |  |
| Thing:weakAlias | name | 384 | Weak alias |  |
| Thing:sourceUrl | url | 4096 | Source link |  |
| Thing:publisher | string | 1024 | Publishing source |  |
| Thing:wikidataId | identifier | 32 | Wikidata ID | format: qid |
| Thing:keywords | string | 1024 | Keywords |  |
| Thing:topics | [topic](https://www.opensanctions.org/reference/#type.topic) | 64 | Topics |  |
| Thing:address | address | 250 | Address |  |
| Thing:addressEntity | [Address](https://www.opensanctions.org/reference/#schema.Address) | 200 | Address | see [Address:things](https://www.opensanctions.org/reference/#prop.Address:things) (inverse) |
| Thing:program | string | 1024 | Program | Regulatory program or sanctions list on which an entity is listed. |
| Thing:notes | text | 65000 | Notes |  |
| Thing:createdAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Created at |  |
| Thing:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Value:amount | number | 250 | Amount |  |
| Value:currency | string | 1024 | Currency |  |
| Value:amountUsd | number | 250 | Amount in USD |  |
| LegalEntity:email | email | 250 | E-Mail | Email address |
| LegalEntity:phone | phone | 32 | Phone | Phone number |
| LegalEntity:website | url | 4096 | Website | Website address |
| LegalEntity:legalForm | string | 1024 | Legal form |  |
| LegalEntity:incorporationDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Incorporation date | The date the legal entity was incorporated |
| LegalEntity:dissolutionDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Dissolution date | The date the legal entity was dissolved, if applicable |
| LegalEntity:status | string | 1024 | Status |  |
| LegalEntity:sector | string | 1024 | Sector |  |
| LegalEntity:classification | string | 1024 | Classification |  |
| Company:registrationNumber | identifier | 64 | Registration number |  |
| LegalEntity:idNumber | identifier | 64 | ID Number | ID number of any applicable ID |
| LegalEntity:taxNumber | identifier | 64 | Tax Number | Tax identification number |
| LegalEntity:vatCode | identifier | 32 | V.A.T. Identifier | (EU) VAT number |
| Company:jurisdiction | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Jurisdiction |  |
| LegalEntity:mainCountry | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country of origin | Primary country of this entity |
| LegalEntity:opencorporatesUrl | url | 4096 | OpenCorporates URL |  |
| LegalEntity:uscCode | identifier | 64 | USCC | Unified Social Credit Identifier format: uscc |
| LegalEntity:icijId | string | 1024 | ICIJ ID | ID according to International Consortium for Investigative Journalists |
| LegalEntity:okpoCode | identifier | 64 | OKPO | Russian industry classifier |
| LegalEntity:innCode | identifier | 32 | INN | Russian company ID format: inn |
| LegalEntity:ogrnCode | identifier | 32 | OGRN | Major State Registration Number format: ogrn |
| LegalEntity:leiCode | identifier | 32 | LEI | Legal Entity Identifier format: lei |
| LegalEntity:dunsCode | identifier | 16 | DUNS | Data Universal Numbering System \- Dun & Bradstreet identifier |
| LegalEntity:uniqueEntityId | identifier | 32 | Unique Entity ID | UEI from SAM.gov format: uei |
| LegalEntity:npiCode | identifier | 16 | NPI | National Provider Identifier format: npi |
| LegalEntity:swiftBic | identifier | 16 | SWIFT/BIC | Bank identifier code format: bic |
| Organization:cageCode | identifier | 16 | CAGE | Commercial and Government Entity Code (CAGE) |
| Organization:permId | identifier | 16 | PermID | LSEG/Refinitiv code for a company |
| Organization:imoNumber | identifier | 16 | IMO Number | format: imo |
| Organization:giiNumber | identifier | 20 | GIIN | Global Intermediary Identification Number |
| Company:cikCode | identifier | 64 | SEC Central Index Key | US SEC Central Index Key |
| Company:kppCode | identifier | 64 | KPP | (RU, КПП) in addition to INN for orgs; reason for registration at FNS |
| Company:bikCode | string | 1024 | BIK | Russian bank account code |
| Company:ticker | identifier | 64 | Stock ticker symbol |  |
| Company:ricCode | identifier | 16 | Reuters Instrument Code |  |

### **CryptoWallet \- Cryptocurrency wallets**

A cryptocurrency wallet is a view on the transactions conducted by one participant on a blockchain / distributed ledger system.

| Extends | [Thing](https://www.opensanctions.org/reference/#schema.Thing) · [Value](https://www.opensanctions.org/reference/#schema.Value) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Thing:name | name | 384 | Name |  |
| Thing:summary | text | 65000 | Summary |  |
| Thing:description | text | 65000 | Description |  |
| Thing:country | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country |  |
| Thing:alias | name | 384 | Other name |  |
| Thing:previousName | name | 384 | Previous name |  |
| Thing:weakAlias | name | 384 | Weak alias |  |
| Thing:sourceUrl | url | 4096 | Source link |  |
| Thing:publisher | string | 1024 | Publishing source |  |
| Thing:wikidataId | identifier | 32 | Wikidata ID | format: qid |
| Thing:keywords | string | 1024 | Keywords |  |
| Thing:topics | [topic](https://www.opensanctions.org/reference/#type.topic) | 64 | Topics |  |
| Thing:address | address | 250 | Address |  |
| Thing:addressEntity | [Address](https://www.opensanctions.org/reference/#schema.Address) | 200 | Address | see [Address:things](https://www.opensanctions.org/reference/#prop.Address:things) (inverse) |
| Thing:program | string | 1024 | Program | Regulatory program or sanctions list on which an entity is listed. |
| Thing:notes | text | 65000 | Notes |  |
| Thing:createdAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Created at |  |
| Thing:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Value:amount | number | 250 | Amount |  |
| Value:currency | string | 1024 | Currency |  |
| Value:amountUsd | number | 250 | Amount in USD |  |
| CryptoWallet:publicKey | identifier | 128 | Address | Public key used to identify the wallet |
| CryptoWallet:managingExchange | string | 1024 | Managing exchange |  |
| CryptoWallet:holder | [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) | 200 | Wallet holder | see [LegalEntity:cryptoWallets](https://www.opensanctions.org/reference/#prop.LegalEntity:cryptoWallets) (inverse) |
| CryptoWallet:balance | number | 250 | Balance |  |

### **Debt \- Debts**

A monetary debt between two parties.

| Extends | [Interval](https://www.opensanctions.org/reference/#schema.Interval) · [Value](https://www.opensanctions.org/reference/#schema.Value) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Interval:startDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Start date |  |
| Interval:endDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | End date |  |
| Interval:date | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Date |  |
| Interval:summary | text | 65000 | Summary |  |
| Interval:description | text | 65000 | Description |  |
| Interval:recordId | string | 1024 | Record ID |  |
| Interval:sourceUrl | url | 4096 | Source link |  |
| Interval:publisher | string | 1024 | Publishing source |  |
| Interval:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Value:amount | number | 250 | Amount |  |
| Value:currency | string | 1024 | Currency |  |
| Value:amountUsd | number | 250 | Amount in USD |  |
| Debt:debtor | [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) | 200 | Debtor | see [LegalEntity:debtDebtor](https://www.opensanctions.org/reference/#prop.LegalEntity:debtDebtor) (inverse) |
| Debt:creditor | [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) | 200 | Creditor | see [LegalEntity:debtCreditor](https://www.opensanctions.org/reference/#prop.LegalEntity:debtCreditor) (inverse) |

### **Directorship \- Directorships**

| Extends | [Interest](https://www.opensanctions.org/reference/#schema.Interest) · [Interval](https://www.opensanctions.org/reference/#schema.Interval) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Interval:startDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Start date |  |
| Interval:endDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | End date |  |
| Interval:date | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Date |  |
| Interval:summary | text | 65000 | Summary |  |
| Interval:description | text | 65000 | Description |  |
| Interval:recordId | string | 1024 | Record ID |  |
| Interval:sourceUrl | url | 4096 | Source link |  |
| Interval:publisher | string | 1024 | Publishing source |  |
| Interval:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Interest:role | string | 1024 | Role |  |
| Interest:status | string | 1024 | Status |  |
| Directorship:director | [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) | 200 | Director | see [LegalEntity:directorshipDirector](https://www.opensanctions.org/reference/#prop.LegalEntity:directorshipDirector) (inverse) |
| Directorship:organization | [Organization](https://www.opensanctions.org/reference/#schema.Organization) | 200 | Organization | see [Organization:directorshipOrganization](https://www.opensanctions.org/reference/#prop.Organization:directorshipOrganization) (inverse) |

### **Employment \- Employments**

| Extends | [Interest](https://www.opensanctions.org/reference/#schema.Interest) · [Interval](https://www.opensanctions.org/reference/#schema.Interval) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Interval:startDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Start date |  |
| Interval:endDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | End date |  |
| Interval:date | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Date |  |
| Interval:summary | text | 65000 | Summary |  |
| Interval:description | text | 65000 | Description |  |
| Interval:recordId | string | 1024 | Record ID |  |
| Interval:sourceUrl | url | 4096 | Source link |  |
| Interval:publisher | string | 1024 | Publishing source |  |
| Interval:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Interest:role | string | 1024 | Role |  |
| Interest:status | string | 1024 | Status |  |
| Employment:employer | [Organization](https://www.opensanctions.org/reference/#schema.Organization) | 200 | Employer | see [Organization:employees](https://www.opensanctions.org/reference/#prop.Organization:employees) (inverse) |
| Employment:employee | [Person](https://www.opensanctions.org/reference/#schema.Person) | 200 | Employee | see [Person:employers](https://www.opensanctions.org/reference/#prop.Person:employers) (inverse) |

### **Family \- Family members**

Family relationship between two people

| Extends | [Interval](https://www.opensanctions.org/reference/#schema.Interval) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Interval:startDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Start date |  |
| Interval:endDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | End date |  |
| Interval:date | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Date |  |
| Interval:summary | text | 65000 | Summary |  |
| Interval:description | text | 65000 | Description |  |
| Interval:recordId | string | 1024 | Record ID |  |
| Interval:sourceUrl | url | 4096 | Source link |  |
| Interval:publisher | string | 1024 | Publishing source |  |
| Interval:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Family:person | [Person](https://www.opensanctions.org/reference/#schema.Person) | 200 | Person | see [Person:familyPerson](https://www.opensanctions.org/reference/#prop.Person:familyPerson) (inverse)The subject of the familial relation. |
| Family:relative | [Person](https://www.opensanctions.org/reference/#schema.Person) | 200 | Relative | see [Person:familyRelative](https://www.opensanctions.org/reference/#prop.Person:familyRelative) (inverse)The relative of the subject person. |
| Family:relationship | string | 1024 | Relationship | Nature of the relationship, from the person's perspective eg. 'mother', where 'relative' is mother of 'person'. |

### **Identification \- Identifications**

An form of identification associated with its holder and some issuing country. This can be used for national ID cards, voter enrollments and similar instruments.

| Extends | [Interval](https://www.opensanctions.org/reference/#schema.Interval) |
| :---: | :---- |
| **Sub-types** | [Passport](https://www.opensanctions.org/reference/#schema.Passport) |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Interval:startDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Start date |  |
| Interval:endDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | End date |  |
| Interval:date | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Date |  |
| Interval:summary | text | 65000 | Summary |  |
| Interval:description | text | 65000 | Description |  |
| Interval:recordId | string | 1024 | Record ID |  |
| Interval:sourceUrl | url | 4096 | Source link |  |
| Interval:publisher | string | 1024 | Publishing source |  |
| Interval:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Identification:holder | [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) | 200 | Identification holder | see [LegalEntity:identification](https://www.opensanctions.org/reference/#prop.LegalEntity:identification) (inverse) |
| Identification:type | string | 1024 | Type |  |
| Identification:country | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country |  |
| Identification:number | identifier | 64 | Document number |  |
| Identification:authority | string | 1024 | Authority |  |

### **Interest \- Interest**

| Extends | [Interval](https://www.opensanctions.org/reference/#schema.Interval) |
| :---: | :---- |
| **Sub-types** | [UnknownLink](https://www.opensanctions.org/reference/#schema.UnknownLink) · [Directorship](https://www.opensanctions.org/reference/#schema.Directorship) · [Employment](https://www.opensanctions.org/reference/#schema.Employment) · [Ownership](https://www.opensanctions.org/reference/#schema.Ownership) · [Membership](https://www.opensanctions.org/reference/#schema.Membership) · [Representation](https://www.opensanctions.org/reference/#schema.Representation) · [Succession](https://www.opensanctions.org/reference/#schema.Succession) |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Interval:startDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Start date |  |
| Interval:endDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | End date |  |
| Interval:date | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Date |  |
| Interval:summary | text | 65000 | Summary |  |
| Interval:description | text | 65000 | Description |  |
| Interval:recordId | string | 1024 | Record ID |  |
| Interval:sourceUrl | url | 4096 | Source link |  |
| Interval:publisher | string | 1024 | Publishing source |  |
| Interval:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Interest:role | string | 1024 | Role |  |
| Interest:status | string | 1024 | Status |  |

### **Interval \- Interval**

An object which is bounded in time.

| Extends |  |
| :---: | :---- |
| **Sub-types** | [UnknownLink](https://www.opensanctions.org/reference/#schema.UnknownLink) · [Passport](https://www.opensanctions.org/reference/#schema.Passport) · [Directorship](https://www.opensanctions.org/reference/#schema.Directorship) · [Associate](https://www.opensanctions.org/reference/#schema.Associate) · [Employment](https://www.opensanctions.org/reference/#schema.Employment) · [Identification](https://www.opensanctions.org/reference/#schema.Identification) · [Ownership](https://www.opensanctions.org/reference/#schema.Ownership) · [Membership](https://www.opensanctions.org/reference/#schema.Membership) · [Debt](https://www.opensanctions.org/reference/#schema.Debt) · [Interest](https://www.opensanctions.org/reference/#schema.Interest) · [Sanction](https://www.opensanctions.org/reference/#schema.Sanction) · [Payment](https://www.opensanctions.org/reference/#schema.Payment) · [Occupancy](https://www.opensanctions.org/reference/#schema.Occupancy) · [Family](https://www.opensanctions.org/reference/#schema.Family) · [Representation](https://www.opensanctions.org/reference/#schema.Representation) · [Succession](https://www.opensanctions.org/reference/#schema.Succession) |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Interval:startDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Start date |  |
| Interval:endDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | End date |  |
| Interval:date | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Date |  |
| Interval:summary | text | 65000 | Summary |  |
| Interval:description | text | 65000 | Description |  |
| Interval:recordId | string | 1024 | Record ID |  |
| Interval:sourceUrl | url | 4096 | Source link |  |
| Interval:publisher | string | 1024 | Publishing source |  |
| Interval:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |

### **LegalEntity \- Legal entities**

Any party to legal proceedings, such as asset ownership, corporate governance or social interactions. Often used when raw data does not specify if something is a person or company.

| Extends | [Thing](https://www.opensanctions.org/reference/#schema.Thing) |
| :---: | :---- |
| **Sub-types** | [PublicBody](https://www.opensanctions.org/reference/#schema.PublicBody) · [Organization](https://www.opensanctions.org/reference/#schema.Organization) · [Company](https://www.opensanctions.org/reference/#schema.Company) · [Person](https://www.opensanctions.org/reference/#schema.Person) |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Thing:name | name | 384 | Name |  |
| Thing:summary | text | 65000 | Summary |  |
| Thing:description | text | 65000 | Description |  |
| Thing:country | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country |  |
| Thing:alias | name | 384 | Other name |  |
| Thing:previousName | name | 384 | Previous name |  |
| Thing:weakAlias | name | 384 | Weak alias |  |
| Thing:sourceUrl | url | 4096 | Source link |  |
| Thing:publisher | string | 1024 | Publishing source |  |
| Thing:wikidataId | identifier | 32 | Wikidata ID | format: qid |
| Thing:keywords | string | 1024 | Keywords |  |
| Thing:topics | [topic](https://www.opensanctions.org/reference/#type.topic) | 64 | Topics |  |
| Thing:address | address | 250 | Address |  |
| Thing:addressEntity | [Address](https://www.opensanctions.org/reference/#schema.Address) | 200 | Address | see [Address:things](https://www.opensanctions.org/reference/#prop.Address:things) (inverse) |
| Thing:program | string | 1024 | Program | Regulatory program or sanctions list on which an entity is listed. |
| Thing:notes | text | 65000 | Notes |  |
| Thing:createdAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Created at |  |
| Thing:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| LegalEntity:email | email | 250 | E-Mail | Email address |
| LegalEntity:phone | phone | 32 | Phone | Phone number |
| LegalEntity:website | url | 4096 | Website | Website address |
| LegalEntity:legalForm | string | 1024 | Legal form |  |
| LegalEntity:incorporationDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Incorporation date | The date the legal entity was incorporated |
| LegalEntity:dissolutionDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Dissolution date | The date the legal entity was dissolved, if applicable |
| LegalEntity:status | string | 1024 | Status |  |
| LegalEntity:sector | string | 1024 | Sector |  |
| LegalEntity:classification | string | 1024 | Classification |  |
| LegalEntity:registrationNumber | identifier | 64 | Registration number | Company registration number |
| LegalEntity:idNumber | identifier | 64 | ID Number | ID number of any applicable ID |
| LegalEntity:taxNumber | identifier | 64 | Tax Number | Tax identification number |
| LegalEntity:vatCode | identifier | 32 | V.A.T. Identifier | (EU) VAT number |
| LegalEntity:jurisdiction | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Jurisdiction | Country or region in which this entity operates |
| LegalEntity:mainCountry | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country of origin | Primary country of this entity |
| LegalEntity:opencorporatesUrl | url | 4096 | OpenCorporates URL |  |
| LegalEntity:uscCode | identifier | 64 | USCC | Unified Social Credit Identifier format: uscc |
| LegalEntity:icijId | string | 1024 | ICIJ ID | ID according to International Consortium for Investigative Journalists |
| LegalEntity:okpoCode | identifier | 64 | OKPO | Russian industry classifier |
| LegalEntity:innCode | identifier | 32 | INN | Russian company ID format: inn |
| LegalEntity:ogrnCode | identifier | 32 | OGRN | Major State Registration Number format: ogrn |
| LegalEntity:leiCode | identifier | 32 | LEI | Legal Entity Identifier format: lei |
| LegalEntity:dunsCode | identifier | 16 | DUNS | Data Universal Numbering System \- Dun & Bradstreet identifier |
| LegalEntity:uniqueEntityId | identifier | 32 | Unique Entity ID | UEI from SAM.gov format: uei |
| LegalEntity:npiCode | identifier | 16 | NPI | National Provider Identifier format: npi |
| LegalEntity:swiftBic | identifier | 16 | SWIFT/BIC | Bank identifier code format: bic |

### **Membership \- Memberships**

| Extends | [Interest](https://www.opensanctions.org/reference/#schema.Interest) · [Interval](https://www.opensanctions.org/reference/#schema.Interval) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Interval:startDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Start date |  |
| Interval:endDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | End date |  |
| Interval:date | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Date |  |
| Interval:summary | text | 65000 | Summary |  |
| Interval:description | text | 65000 | Description |  |
| Interval:recordId | string | 1024 | Record ID |  |
| Interval:sourceUrl | url | 4096 | Source link |  |
| Interval:publisher | string | 1024 | Publishing source |  |
| Interval:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Interest:role | string | 1024 | Role |  |
| Interest:status | string | 1024 | Status |  |
| Membership:member | [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) | 200 | Member | see [LegalEntity:membershipMember](https://www.opensanctions.org/reference/#prop.LegalEntity:membershipMember) (inverse) |
| Membership:organization | [Organization](https://www.opensanctions.org/reference/#schema.Organization) | 200 | Organization | see [Organization:membershipOrganization](https://www.opensanctions.org/reference/#prop.Organization:membershipOrganization) (inverse) |

### **Occupancy \- Occupancies**

The occupation of a position by a person for a specific period of time.

| Extends | [Interval](https://www.opensanctions.org/reference/#schema.Interval) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Interval:startDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Start date |  |
| Interval:endDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | End date |  |
| Interval:date | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Date |  |
| Interval:summary | text | 65000 | Summary |  |
| Interval:description | text | 65000 | Description |  |
| Interval:recordId | string | 1024 | Record ID |  |
| Interval:sourceUrl | url | 4096 | Source link |  |
| Interval:publisher | string | 1024 | Publishing source |  |
| Interval:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Occupancy:holder | [Person](https://www.opensanctions.org/reference/#schema.Person) | 200 | Holder | see [Person:positionOccupancies](https://www.opensanctions.org/reference/#prop.Person:positionOccupancies) (inverse) |
| Occupancy:post | [Position](https://www.opensanctions.org/reference/#schema.Position) | 200 | Position occupied | see [Position:occupancies](https://www.opensanctions.org/reference/#prop.Position:occupancies) (inverse) |
| Occupancy:declarationDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Declaration date |  |
| Occupancy:status | string | 1024 | Status |  |

### **Organization \- Organizations**

Any type of incorporated entity that cannot be owned by another (see Company). This might include charities, foundations or state-owned enterprises, depending on their jurisdiction.

| Extends | [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) · [Thing](https://www.opensanctions.org/reference/#schema.Thing) |
| :---: | :---- |
| **Sub-types** | [PublicBody](https://www.opensanctions.org/reference/#schema.PublicBody) · [Company](https://www.opensanctions.org/reference/#schema.Company) |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Thing:name | name | 384 | Name |  |
| Thing:summary | text | 65000 | Summary |  |
| Thing:description | text | 65000 | Description |  |
| Thing:country | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country |  |
| Thing:alias | name | 384 | Other name |  |
| Thing:previousName | name | 384 | Previous name |  |
| Thing:weakAlias | name | 384 | Weak alias |  |
| Thing:sourceUrl | url | 4096 | Source link |  |
| Thing:publisher | string | 1024 | Publishing source |  |
| Thing:wikidataId | identifier | 32 | Wikidata ID | format: qid |
| Thing:keywords | string | 1024 | Keywords |  |
| Thing:topics | [topic](https://www.opensanctions.org/reference/#type.topic) | 64 | Topics |  |
| Thing:address | address | 250 | Address |  |
| Thing:addressEntity | [Address](https://www.opensanctions.org/reference/#schema.Address) | 200 | Address | see [Address:things](https://www.opensanctions.org/reference/#prop.Address:things) (inverse) |
| Thing:program | string | 1024 | Program | Regulatory program or sanctions list on which an entity is listed. |
| Thing:notes | text | 65000 | Notes |  |
| Thing:createdAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Created at |  |
| Thing:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| LegalEntity:email | email | 250 | E-Mail | Email address |
| LegalEntity:phone | phone | 32 | Phone | Phone number |
| LegalEntity:website | url | 4096 | Website | Website address |
| LegalEntity:legalForm | string | 1024 | Legal form |  |
| LegalEntity:incorporationDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Incorporation date | The date the legal entity was incorporated |
| LegalEntity:dissolutionDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Dissolution date | The date the legal entity was dissolved, if applicable |
| LegalEntity:status | string | 1024 | Status |  |
| LegalEntity:sector | string | 1024 | Sector |  |
| LegalEntity:classification | string | 1024 | Classification |  |
| LegalEntity:registrationNumber | identifier | 64 | Registration number | Company registration number |
| LegalEntity:idNumber | identifier | 64 | ID Number | ID number of any applicable ID |
| LegalEntity:taxNumber | identifier | 64 | Tax Number | Tax identification number |
| LegalEntity:vatCode | identifier | 32 | V.A.T. Identifier | (EU) VAT number |
| LegalEntity:jurisdiction | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Jurisdiction | Country or region in which this entity operates |
| LegalEntity:mainCountry | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country of origin | Primary country of this entity |
| LegalEntity:opencorporatesUrl | url | 4096 | OpenCorporates URL |  |
| LegalEntity:uscCode | identifier | 64 | USCC | Unified Social Credit Identifier format: uscc |
| LegalEntity:icijId | string | 1024 | ICIJ ID | ID according to International Consortium for Investigative Journalists |
| LegalEntity:okpoCode | identifier | 64 | OKPO | Russian industry classifier |
| LegalEntity:innCode | identifier | 32 | INN | Russian company ID format: inn |
| LegalEntity:ogrnCode | identifier | 32 | OGRN | Major State Registration Number format: ogrn |
| LegalEntity:leiCode | identifier | 32 | LEI | Legal Entity Identifier format: lei |
| LegalEntity:dunsCode | identifier | 16 | DUNS | Data Universal Numbering System \- Dun & Bradstreet identifier |
| LegalEntity:uniqueEntityId | identifier | 32 | Unique Entity ID | UEI from SAM.gov format: uei |
| LegalEntity:npiCode | identifier | 16 | NPI | National Provider Identifier format: npi |
| LegalEntity:swiftBic | identifier | 16 | SWIFT/BIC | Bank identifier code format: bic |
| Organization:cageCode | identifier | 16 | CAGE | Commercial and Government Entity Code (CAGE) |
| Organization:permId | identifier | 16 | PermID | LSEG/Refinitiv code for a company |
| Organization:imoNumber | identifier | 16 | IMO Number | format: imo |
| Organization:giiNumber | identifier | 20 | GIIN | Global Intermediary Identification Number |

### **Ownership \- Ownerships**

| Extends | [Interest](https://www.opensanctions.org/reference/#schema.Interest) · [Interval](https://www.opensanctions.org/reference/#schema.Interval) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Interval:startDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Start date |  |
| Interval:endDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | End date |  |
| Interval:date | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Date |  |
| Interval:summary | text | 65000 | Summary |  |
| Interval:description | text | 65000 | Description |  |
| Interval:recordId | string | 1024 | Record ID |  |
| Interval:sourceUrl | url | 4096 | Source link |  |
| Interval:publisher | string | 1024 | Publishing source |  |
| Interval:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Interest:role | string | 1024 | Role |  |
| Interest:status | string | 1024 | Status |  |
| Ownership:owner | [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) | 200 | Owner | see [LegalEntity:ownershipOwner](https://www.opensanctions.org/reference/#prop.LegalEntity:ownershipOwner) (inverse) |
| Ownership:asset | [Asset](https://www.opensanctions.org/reference/#schema.Asset) | 200 | Asset | see [Asset:ownershipAsset](https://www.opensanctions.org/reference/#prop.Asset:ownershipAsset) (inverse) |
| Ownership:percentage | string | 1024 | Percentage held |  |
| Ownership:sharesCount | string | 1024 | Number of shares |  |
| Ownership:sharesValue | string | 1024 | Value of shares |  |
| Ownership:sharesCurrency | string | 1024 | Currency of shares |  |

### **Passport \- Passports**

An passport held by a person.

| Extends | [Identification](https://www.opensanctions.org/reference/#schema.Identification) · [Interval](https://www.opensanctions.org/reference/#schema.Interval) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Interval:startDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Start date |  |
| Interval:endDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | End date |  |
| Interval:date | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Date |  |
| Interval:summary | text | 65000 | Summary |  |
| Interval:description | text | 65000 | Description |  |
| Interval:recordId | string | 1024 | Record ID |  |
| Interval:sourceUrl | url | 4096 | Source link |  |
| Interval:publisher | string | 1024 | Publishing source |  |
| Interval:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Identification:holder | [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) | 200 | Identification holder | see [LegalEntity:identification](https://www.opensanctions.org/reference/#prop.LegalEntity:identification) (inverse) |
| Identification:type | string | 1024 | Type |  |
| Identification:country | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country |  |
| Identification:number | identifier | 64 | Document number |  |
| Identification:authority | string | 1024 | Authority |  |

### **Payment \- Payments**

A monetary payment between two parties.

| Extends | [Interval](https://www.opensanctions.org/reference/#schema.Interval) · [Value](https://www.opensanctions.org/reference/#schema.Value) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Interval:startDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Start date |  |
| Interval:endDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | End date |  |
| Interval:date | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Date |  |
| Interval:summary | text | 65000 | Summary |  |
| Interval:description | text | 65000 | Description |  |
| Interval:recordId | string | 1024 | Record ID |  |
| Interval:sourceUrl | url | 4096 | Source link |  |
| Interval:publisher | string | 1024 | Publishing source |  |
| Interval:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Value:amount | number | 250 | Amount |  |
| Value:currency | string | 1024 | Currency |  |
| Value:amountUsd | number | 250 | Amount in USD |  |
| Payment:payer | [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) | 200 | Payer | see [LegalEntity:paymentPayer](https://www.opensanctions.org/reference/#prop.LegalEntity:paymentPayer) (inverse) |
| Payment:beneficiary | [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) | 200 | Beneficiary | see [LegalEntity:paymentBeneficiary](https://www.opensanctions.org/reference/#prop.LegalEntity:paymentBeneficiary) (inverse) |

### **Person \- People**

A natural person, as opposed to a corporation of some type.

| Extends | [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) · [Thing](https://www.opensanctions.org/reference/#schema.Thing) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Thing:name | name | 384 | Name |  |
| Thing:summary | text | 65000 | Summary |  |
| Thing:description | text | 65000 | Description |  |
| Thing:country | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country |  |
| Thing:alias | name | 384 | Other name |  |
| Thing:previousName | name | 384 | Previous name |  |
| Thing:weakAlias | name | 384 | Weak alias |  |
| Thing:sourceUrl | url | 4096 | Source link |  |
| Thing:publisher | string | 1024 | Publishing source |  |
| Thing:wikidataId | identifier | 32 | Wikidata ID | format: qid |
| Thing:keywords | string | 1024 | Keywords |  |
| Thing:topics | [topic](https://www.opensanctions.org/reference/#type.topic) | 64 | Topics |  |
| Thing:address | address | 250 | Address |  |
| Thing:addressEntity | [Address](https://www.opensanctions.org/reference/#schema.Address) | 200 | Address | see [Address:things](https://www.opensanctions.org/reference/#prop.Address:things) (inverse) |
| Thing:program | string | 1024 | Program | Regulatory program or sanctions list on which an entity is listed. |
| Thing:notes | text | 65000 | Notes |  |
| Thing:createdAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Created at |  |
| Thing:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| LegalEntity:email | email | 250 | E-Mail | Email address |
| LegalEntity:phone | phone | 32 | Phone | Phone number |
| LegalEntity:website | url | 4096 | Website | Website address |
| LegalEntity:legalForm | string | 1024 | Legal form |  |
| LegalEntity:incorporationDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Incorporation date | The date the legal entity was incorporated |
| LegalEntity:dissolutionDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Dissolution date | The date the legal entity was dissolved, if applicable |
| LegalEntity:status | string | 1024 | Status |  |
| LegalEntity:sector | string | 1024 | Sector |  |
| LegalEntity:classification | string | 1024 | Classification |  |
| LegalEntity:registrationNumber | identifier | 64 | Registration number | Company registration number |
| LegalEntity:idNumber | identifier | 64 | ID Number | ID number of any applicable ID |
| LegalEntity:taxNumber | identifier | 64 | Tax Number | Tax identification number |
| LegalEntity:vatCode | identifier | 32 | V.A.T. Identifier | (EU) VAT number |
| LegalEntity:jurisdiction | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Jurisdiction | Country or region in which this entity operates |
| LegalEntity:mainCountry | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country of origin | Primary country of this entity |
| LegalEntity:opencorporatesUrl | url | 4096 | OpenCorporates URL |  |
| LegalEntity:uscCode | identifier | 64 | USCC | Unified Social Credit Identifier format: uscc |
| LegalEntity:icijId | string | 1024 | ICIJ ID | ID according to International Consortium for Investigative Journalists |
| LegalEntity:okpoCode | identifier | 64 | OKPO | Russian industry classifier |
| LegalEntity:innCode | identifier | 32 | INN | Russian company ID format: inn |
| LegalEntity:ogrnCode | identifier | 32 | OGRN | Major State Registration Number format: ogrn |
| LegalEntity:leiCode | identifier | 32 | LEI | Legal Entity Identifier format: lei |
| LegalEntity:dunsCode | identifier | 16 | DUNS | Data Universal Numbering System \- Dun & Bradstreet identifier |
| LegalEntity:uniqueEntityId | identifier | 32 | Unique Entity ID | UEI from SAM.gov format: uei |
| LegalEntity:npiCode | identifier | 16 | NPI | National Provider Identifier format: npi |
| LegalEntity:swiftBic | identifier | 16 | SWIFT/BIC | Bank identifier code format: bic |
| Person:title | string | 1024 | Title |  |
| Person:firstName | string | 1024 | First name |  |
| Person:secondName | string | 1024 | Second name |  |
| Person:middleName | string | 1024 | Middle name |  |
| Person:fatherName | string | 1024 | Patronymic |  |
| Person:motherName | string | 1024 | Matronymic |  |
| Person:lastName | string | 1024 | Last name |  |
| Person:nameSuffix | string | 1024 | Name suffix |  |
| Person:birthDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Birth date |  |
| Person:birthPlace | string | 1024 | Place of birth |  |
| Person:birthCountry | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country of birth |  |
| Person:deathDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Death date |  |
| Person:position | string | 1024 | Position |  |
| Person:nationality | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Nationality |  |
| Person:citizenship | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Citizenship |  |
| Person:passportNumber | identifier | 64 | Passport number |  |
| Person:socialSecurityNumber | identifier | 64 | Social security number | format: ssn |
| Person:gender | gender | 16 | Gender |  |
| Person:ethnicity | string | 1024 | Ethnicity |  |
| Person:height | number | 250 | Height |  |
| Person:weight | number | 250 | Weight |  |
| Person:eyeColor | string | 1024 | Eye color |  |
| Person:hairColor | string | 1024 | Hair color |  |
| Person:appearance | string | 1024 | Physical appearance |  |
| Person:religion | string | 1024 | Religion |  |
| Person:political | string | 1024 | Political association |  |
| Person:education | string | 1024 | Education |  |

### **Position \- Positions**

A post, role or position within an organization or body. This describes a position one or more people may occupy and not the occupation of the post by a specific individual at a specific point in time. 'subnationalArea' should be used to further restrict the scope of the position. It should not simply represent some regional aspect of the role \- e.g. the constituency of a national member of parliament \- when their legislative jurisdiction is nationwide.

| Extends | [Thing](https://www.opensanctions.org/reference/#schema.Thing) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Thing:name | name | 384 | Name |  |
| Thing:summary | text | 65000 | Summary |  |
| Thing:description | text | 65000 | Description |  |
| Thing:country | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country |  |
| Thing:alias | name | 384 | Other name |  |
| Thing:previousName | name | 384 | Previous name |  |
| Thing:weakAlias | name | 384 | Weak alias |  |
| Thing:sourceUrl | url | 4096 | Source link |  |
| Thing:publisher | string | 1024 | Publishing source |  |
| Thing:wikidataId | identifier | 32 | Wikidata ID | format: qid |
| Thing:keywords | string | 1024 | Keywords |  |
| Thing:topics | [topic](https://www.opensanctions.org/reference/#type.topic) | 64 | Topics |  |
| Thing:address | address | 250 | Address |  |
| Thing:addressEntity | [Address](https://www.opensanctions.org/reference/#schema.Address) | 200 | Address | see [Address:things](https://www.opensanctions.org/reference/#prop.Address:things) (inverse) |
| Thing:program | string | 1024 | Program | Regulatory program or sanctions list on which an entity is listed. |
| Thing:notes | text | 65000 | Notes |  |
| Thing:createdAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Created at |  |
| Thing:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Position:inceptionDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Inception date |  |
| Position:dissolutionDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Dissolution date |  |
| Position:subnationalArea | string | 1024 | Subnational jurisdiction name or code |  |

### **PublicBody \- Public bodies**

A public body, such as a ministry, department or state company.

| Extends | [Organization](https://www.opensanctions.org/reference/#schema.Organization) · [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) · [Thing](https://www.opensanctions.org/reference/#schema.Thing) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Thing:name | name | 384 | Name |  |
| Thing:summary | text | 65000 | Summary |  |
| Thing:description | text | 65000 | Description |  |
| Thing:country | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country |  |
| Thing:alias | name | 384 | Other name |  |
| Thing:previousName | name | 384 | Previous name |  |
| Thing:weakAlias | name | 384 | Weak alias |  |
| Thing:sourceUrl | url | 4096 | Source link |  |
| Thing:publisher | string | 1024 | Publishing source |  |
| Thing:wikidataId | identifier | 32 | Wikidata ID | format: qid |
| Thing:keywords | string | 1024 | Keywords |  |
| Thing:topics | [topic](https://www.opensanctions.org/reference/#type.topic) | 64 | Topics |  |
| Thing:address | address | 250 | Address |  |
| Thing:addressEntity | [Address](https://www.opensanctions.org/reference/#schema.Address) | 200 | Address | see [Address:things](https://www.opensanctions.org/reference/#prop.Address:things) (inverse) |
| Thing:program | string | 1024 | Program | Regulatory program or sanctions list on which an entity is listed. |
| Thing:notes | text | 65000 | Notes |  |
| Thing:createdAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Created at |  |
| Thing:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| LegalEntity:email | email | 250 | E-Mail | Email address |
| LegalEntity:phone | phone | 32 | Phone | Phone number |
| LegalEntity:website | url | 4096 | Website | Website address |
| LegalEntity:legalForm | string | 1024 | Legal form |  |
| LegalEntity:incorporationDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Incorporation date | The date the legal entity was incorporated |
| LegalEntity:dissolutionDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Dissolution date | The date the legal entity was dissolved, if applicable |
| LegalEntity:status | string | 1024 | Status |  |
| LegalEntity:sector | string | 1024 | Sector |  |
| LegalEntity:classification | string | 1024 | Classification |  |
| LegalEntity:registrationNumber | identifier | 64 | Registration number | Company registration number |
| LegalEntity:idNumber | identifier | 64 | ID Number | ID number of any applicable ID |
| LegalEntity:taxNumber | identifier | 64 | Tax Number | Tax identification number |
| LegalEntity:vatCode | identifier | 32 | V.A.T. Identifier | (EU) VAT number |
| LegalEntity:jurisdiction | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Jurisdiction | Country or region in which this entity operates |
| LegalEntity:mainCountry | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country of origin | Primary country of this entity |
| LegalEntity:opencorporatesUrl | url | 4096 | OpenCorporates URL |  |
| LegalEntity:uscCode | identifier | 64 | USCC | Unified Social Credit Identifier format: uscc |
| LegalEntity:icijId | string | 1024 | ICIJ ID | ID according to International Consortium for Investigative Journalists |
| LegalEntity:okpoCode | identifier | 64 | OKPO | Russian industry classifier |
| LegalEntity:innCode | identifier | 32 | INN | Russian company ID format: inn |
| LegalEntity:ogrnCode | identifier | 32 | OGRN | Major State Registration Number format: ogrn |
| LegalEntity:leiCode | identifier | 32 | LEI | Legal Entity Identifier format: lei |
| LegalEntity:dunsCode | identifier | 16 | DUNS | Data Universal Numbering System \- Dun & Bradstreet identifier |
| LegalEntity:uniqueEntityId | identifier | 32 | Unique Entity ID | UEI from SAM.gov format: uei |
| LegalEntity:npiCode | identifier | 16 | NPI | National Provider Identifier format: npi |
| LegalEntity:swiftBic | identifier | 16 | SWIFT/BIC | Bank identifier code format: bic |
| Organization:cageCode | identifier | 16 | CAGE | Commercial and Government Entity Code (CAGE) |
| Organization:permId | identifier | 16 | PermID | LSEG/Refinitiv code for a company |
| Organization:imoNumber | identifier | 16 | IMO Number | format: imo |
| Organization:giiNumber | identifier | 20 | GIIN | Global Intermediary Identification Number |

### **Representation \- Representations**

A mediatory, intermediary, middleman, or broker acting on behalf of a legal entity.

| Extends | [Interest](https://www.opensanctions.org/reference/#schema.Interest) · [Interval](https://www.opensanctions.org/reference/#schema.Interval) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Interval:startDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Start date |  |
| Interval:endDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | End date |  |
| Interval:date | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Date |  |
| Interval:summary | text | 65000 | Summary |  |
| Interval:description | text | 65000 | Description |  |
| Interval:recordId | string | 1024 | Record ID |  |
| Interval:sourceUrl | url | 4096 | Source link |  |
| Interval:publisher | string | 1024 | Publishing source |  |
| Interval:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Interest:role | string | 1024 | Role |  |
| Interest:status | string | 1024 | Status |  |
| Representation:agent | [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) | 200 | Agent | see [LegalEntity:agencyClient](https://www.opensanctions.org/reference/#prop.LegalEntity:agencyClient) (inverse) |
| Representation:client | [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) | 200 | Client | see [LegalEntity:agentRepresentation](https://www.opensanctions.org/reference/#prop.LegalEntity:agentRepresentation) (inverse) |

### **Sanction \- Sanctions**

A sanction designation

| Extends | [Interval](https://www.opensanctions.org/reference/#schema.Interval) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Interval:startDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Start date |  |
| Interval:endDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | End date |  |
| Interval:date | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Date |  |
| Interval:summary | text | 65000 | Summary |  |
| Interval:description | text | 65000 | Description |  |
| Interval:recordId | string | 1024 | Record ID |  |
| Interval:sourceUrl | url | 4096 | Source link |  |
| Interval:publisher | string | 1024 | Publishing source |  |
| Interval:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Sanction:entity | [Thing](https://www.opensanctions.org/reference/#schema.Thing) | 200 | Entity | see [Thing:sanctions](https://www.opensanctions.org/reference/#prop.Thing:sanctions) (inverse) |
| Sanction:authority | string | 1024 | Authority |  |
| Sanction:authorityId | identifier | 64 | Authority-issued identifier |  |
| Sanction:unscId | identifier | 16 | UN SC identifier |  |
| Sanction:program | string | 1024 | Program |  |
| Sanction:programId | identifier | 64 | Program ID |  |
| Sanction:programUrl | url | 4096 | Program URL |  |
| Sanction:provisions | string | 1024 | Scope of sanctions |  |
| Sanction:status | string | 1024 | Status |  |
| Sanction:duration | number | 250 | Duration |  |
| Sanction:reason | text | 65000 | Reason |  |
| Sanction:country | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country |  |
| Sanction:listingDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Listing date |  |

### **Security \- Securities**

A tradeable financial asset.

| Extends | [Asset](https://www.opensanctions.org/reference/#schema.Asset) · [Thing](https://www.opensanctions.org/reference/#schema.Thing) · [Value](https://www.opensanctions.org/reference/#schema.Value) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Thing:name | name | 384 | Name |  |
| Thing:summary | text | 65000 | Summary |  |
| Thing:description | text | 65000 | Description |  |
| Thing:country | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country |  |
| Thing:alias | name | 384 | Other name |  |
| Thing:previousName | name | 384 | Previous name |  |
| Thing:weakAlias | name | 384 | Weak alias |  |
| Thing:sourceUrl | url | 4096 | Source link |  |
| Thing:publisher | string | 1024 | Publishing source |  |
| Thing:wikidataId | identifier | 32 | Wikidata ID | format: qid |
| Thing:keywords | string | 1024 | Keywords |  |
| Thing:topics | [topic](https://www.opensanctions.org/reference/#type.topic) | 64 | Topics |  |
| Thing:address | address | 250 | Address |  |
| Thing:addressEntity | [Address](https://www.opensanctions.org/reference/#schema.Address) | 200 | Address | see [Address:things](https://www.opensanctions.org/reference/#prop.Address:things) (inverse) |
| Thing:program | string | 1024 | Program | Regulatory program or sanctions list on which an entity is listed. |
| Thing:notes | text | 65000 | Notes |  |
| Thing:createdAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Created at |  |
| Thing:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Value:amount | number | 250 | Amount |  |
| Value:currency | string | 1024 | Currency |  |
| Value:amountUsd | number | 250 | Amount in USD |  |
| Security:isin | identifier | 16 | ISIN | International Securities Identification Number format: isin |
| Security:registrationNumber | identifier | 64 | Registration number |  |
| Security:ticker | identifier | 64 | Stock ticker symbol |  |
| Security:figiCode | identifier | 16 | Financial Instrument Global Identifier | format: figi |
| Security:issuer | [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) | 200 | Issuer | see [LegalEntity:securities](https://www.opensanctions.org/reference/#prop.LegalEntity:securities) (inverse) |
| Security:issueDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Date issued |  |
| Security:maturityDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Maturity date |  |
| Security:type | string | 1024 | Type |  |
| Security:classification | string | 1024 | Classification |  |

### **Succession \- Successions**

Two entities that legally succeed each other.

| Extends | [Interest](https://www.opensanctions.org/reference/#schema.Interest) · [Interval](https://www.opensanctions.org/reference/#schema.Interval) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Interval:startDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Start date |  |
| Interval:endDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | End date |  |
| Interval:date | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Date |  |
| Interval:summary | text | 65000 | Summary |  |
| Interval:description | text | 65000 | Description |  |
| Interval:recordId | string | 1024 | Record ID |  |
| Interval:sourceUrl | url | 4096 | Source link |  |
| Interval:publisher | string | 1024 | Publishing source |  |
| Interval:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Interest:role | string | 1024 | Role |  |
| Interest:status | string | 1024 | Status |  |
| Succession:predecessor | [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) | 200 | Predecessor | see [LegalEntity:successors](https://www.opensanctions.org/reference/#prop.LegalEntity:successors) (inverse) |
| Succession:successor | [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) | 200 | Successor | see [LegalEntity:predecessors](https://www.opensanctions.org/reference/#prop.LegalEntity:predecessors) (inverse) |

### **Thing \- Thing**

| Extends |  |
| :---: | :---- |
| **Sub-types** | [Position](https://www.opensanctions.org/reference/#schema.Position) · [PublicBody](https://www.opensanctions.org/reference/#schema.PublicBody) · [Airplane](https://www.opensanctions.org/reference/#schema.Airplane) · [Security](https://www.opensanctions.org/reference/#schema.Security) · [Vehicle](https://www.opensanctions.org/reference/#schema.Vehicle) · [Vessel](https://www.opensanctions.org/reference/#schema.Vessel) · [Address](https://www.opensanctions.org/reference/#schema.Address) · [Organization](https://www.opensanctions.org/reference/#schema.Organization) · [Asset](https://www.opensanctions.org/reference/#schema.Asset) · [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) · [Company](https://www.opensanctions.org/reference/#schema.Company) · [CryptoWallet](https://www.opensanctions.org/reference/#schema.CryptoWallet) · [Person](https://www.opensanctions.org/reference/#schema.Person) |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Thing:name | name | 384 | Name |  |
| Thing:summary | text | 65000 | Summary |  |
| Thing:description | text | 65000 | Description |  |
| Thing:country | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country |  |
| Thing:alias | name | 384 | Other name |  |
| Thing:previousName | name | 384 | Previous name |  |
| Thing:weakAlias | name | 384 | Weak alias |  |
| Thing:sourceUrl | url | 4096 | Source link |  |
| Thing:publisher | string | 1024 | Publishing source |  |
| Thing:wikidataId | identifier | 32 | Wikidata ID | format: qid |
| Thing:keywords | string | 1024 | Keywords |  |
| Thing:topics | [topic](https://www.opensanctions.org/reference/#type.topic) | 64 | Topics |  |
| Thing:address | address | 250 | Address |  |
| Thing:addressEntity | [Address](https://www.opensanctions.org/reference/#schema.Address) | 200 | Address | see [Address:things](https://www.opensanctions.org/reference/#prop.Address:things) (inverse) |
| Thing:program | string | 1024 | Program | Regulatory program or sanctions list on which an entity is listed. |
| Thing:notes | text | 65000 | Notes |  |
| Thing:createdAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Created at |  |
| Thing:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |

### **UnknownLink \- Other links**

| Extends | [Interest](https://www.opensanctions.org/reference/#schema.Interest) · [Interval](https://www.opensanctions.org/reference/#schema.Interval) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Interval:startDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Start date |  |
| Interval:endDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | End date |  |
| Interval:date | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Date |  |
| Interval:summary | text | 65000 | Summary |  |
| Interval:description | text | 65000 | Description |  |
| Interval:recordId | string | 1024 | Record ID |  |
| Interval:sourceUrl | url | 4096 | Source link |  |
| Interval:publisher | string | 1024 | Publishing source |  |
| Interval:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Interest:role | string | 1024 | Role |  |
| Interest:status | string | 1024 | Status |  |
| UnknownLink:subject | [Thing](https://www.opensanctions.org/reference/#schema.Thing) | 200 | Subject | see [Thing:unknownLinkTo](https://www.opensanctions.org/reference/#prop.Thing:unknownLinkTo) (inverse) |
| UnknownLink:object | [Thing](https://www.opensanctions.org/reference/#schema.Thing) | 200 | Object | see [Thing:unknownLinkFrom](https://www.opensanctions.org/reference/#prop.Thing:unknownLinkFrom) (inverse) |

### **Value \- Values**

| Extends |  |
| :---: | :---- |
| **Sub-types** | [Airplane](https://www.opensanctions.org/reference/#schema.Airplane) · [Security](https://www.opensanctions.org/reference/#schema.Security) · [Vehicle](https://www.opensanctions.org/reference/#schema.Vehicle) · [Vessel](https://www.opensanctions.org/reference/#schema.Vessel) · [Debt](https://www.opensanctions.org/reference/#schema.Debt) · [Asset](https://www.opensanctions.org/reference/#schema.Asset) · [Payment](https://www.opensanctions.org/reference/#schema.Payment) · [Company](https://www.opensanctions.org/reference/#schema.Company) · [CryptoWallet](https://www.opensanctions.org/reference/#schema.CryptoWallet) |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Value:amount | number | 250 | Amount |  |
| Value:currency | string | 1024 | Currency |  |
| Value:amountUsd | number | 250 | Amount in USD |  |

### **Vehicle \- Vehicles**

| Extends | [Asset](https://www.opensanctions.org/reference/#schema.Asset) · [Thing](https://www.opensanctions.org/reference/#schema.Thing) · [Value](https://www.opensanctions.org/reference/#schema.Value) |
| :---: | :---- |
| **Sub-types** | [Airplane](https://www.opensanctions.org/reference/#schema.Airplane) · [Vessel](https://www.opensanctions.org/reference/#schema.Vessel) |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Thing:name | name | 384 | Name |  |
| Thing:summary | text | 65000 | Summary |  |
| Thing:description | text | 65000 | Description |  |
| Thing:country | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country |  |
| Thing:alias | name | 384 | Other name |  |
| Thing:previousName | name | 384 | Previous name |  |
| Thing:weakAlias | name | 384 | Weak alias |  |
| Thing:sourceUrl | url | 4096 | Source link |  |
| Thing:publisher | string | 1024 | Publishing source |  |
| Thing:wikidataId | identifier | 32 | Wikidata ID | format: qid |
| Thing:keywords | string | 1024 | Keywords |  |
| Thing:topics | [topic](https://www.opensanctions.org/reference/#type.topic) | 64 | Topics |  |
| Thing:address | address | 250 | Address |  |
| Thing:addressEntity | [Address](https://www.opensanctions.org/reference/#schema.Address) | 200 | Address | see [Address:things](https://www.opensanctions.org/reference/#prop.Address:things) (inverse) |
| Thing:program | string | 1024 | Program | Regulatory program or sanctions list on which an entity is listed. |
| Thing:notes | text | 65000 | Notes |  |
| Thing:createdAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Created at |  |
| Thing:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Value:amount | number | 250 | Amount |  |
| Value:currency | string | 1024 | Currency |  |
| Value:amountUsd | number | 250 | Amount in USD |  |
| Vehicle:registrationNumber | identifier | 64 | Registration number |  |
| Vehicle:type | string | 1024 | Type |  |
| Vehicle:model | string | 1024 | Model |  |
| Vehicle:owner | [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) | 200 | Owner | see [LegalEntity:ownedVehicles](https://www.opensanctions.org/reference/#prop.LegalEntity:ownedVehicles) (inverse) |
| Vehicle:buildDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Build Date |  |

### **Vessel \- Vessels**

A boat or ship. Typically flying some sort of national flag.

| Extends | [Vehicle](https://www.opensanctions.org/reference/#schema.Vehicle) · [Asset](https://www.opensanctions.org/reference/#schema.Asset) · [Thing](https://www.opensanctions.org/reference/#schema.Thing) · [Value](https://www.opensanctions.org/reference/#schema.Value) |
| :---: | :---- |

| Property | Type | Length | Title | Description |
| ----- | ----- | ----- | ----- | ----- |
| Thing:name | name | 384 | Name |  |
| Thing:summary | text | 65000 | Summary |  |
| Thing:description | text | 65000 | Description |  |
| Thing:country | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Country |  |
| Thing:alias | name | 384 | Other name |  |
| Thing:previousName | name | 384 | Previous name |  |
| Thing:weakAlias | name | 384 | Weak alias |  |
| Thing:sourceUrl | url | 4096 | Source link |  |
| Thing:publisher | string | 1024 | Publishing source |  |
| Thing:wikidataId | identifier | 32 | Wikidata ID | format: qid |
| Thing:keywords | string | 1024 | Keywords |  |
| Thing:topics | [topic](https://www.opensanctions.org/reference/#type.topic) | 64 | Topics |  |
| Thing:address | address | 250 | Address |  |
| Thing:addressEntity | [Address](https://www.opensanctions.org/reference/#schema.Address) | 200 | Address | see [Address:things](https://www.opensanctions.org/reference/#prop.Address:things) (inverse) |
| Thing:program | string | 1024 | Program | Regulatory program or sanctions list on which an entity is listed. |
| Thing:notes | text | 65000 | Notes |  |
| Thing:createdAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Created at |  |
| Thing:modifiedAt | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Modified on |  |
| Value:amount | number | 250 | Amount |  |
| Value:currency | string | 1024 | Currency |  |
| Value:amountUsd | number | 250 | Amount in USD |  |
| Vehicle:registrationNumber | identifier | 64 | Registration number |  |
| Vehicle:type | string | 1024 | Type |  |
| Vehicle:model | string | 1024 | Model |  |
| Vehicle:owner | [LegalEntity](https://www.opensanctions.org/reference/#schema.LegalEntity) | 200 | Owner | see [LegalEntity:ownedVehicles](https://www.opensanctions.org/reference/#prop.LegalEntity:ownedVehicles) (inverse) |
| Vehicle:buildDate | [date](https://www.opensanctions.org/reference/#type.date) | 32 | Build Date |  |
| Vessel:imoNumber | identifier | 16 | IMO Number | format: imo |
| Vessel:flag | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Flag |  |
| Vessel:tonnage | number | 250 | Tonnage |  |
| Vessel:grossRegisteredTonnage | number | 250 | Gross Registered Tonnage |  |
| Vessel:callSign | identifier | 64 | Call Sign |  |
| Vessel:pastFlags | [country](https://www.opensanctions.org/reference/#type.country) | 16 | Past Flags |  |
| Vessel:mmsi | identifier | 16 | MMSI |  |

## **Type definitions**

Schema properties have specific types which define the range of valid values they can hold. Below are the enumerated values for some of the types. Other types perform algorithmic validation, e.g. for phone numbers, URLs or email addresses.

### **Entities**

Entity references are used by one [entity](https://www.opensanctions.org/docs/entities/) to reference another and thus create a link between the two. Take note of the [guidance on entity identifiers](https://www.opensanctions.org/docs/identifiers/) to understand how entity IDs change as incoming records are deduplicated.

### **Topics**

Topics are used to tag other entities \- mainly organizations and people \- with risk categories, e.g. to designate an individual as a politician, terrorist or to hint that a certain company is a bank. [Read more about topics](https://www.opensanctions.org/docs/topics/) and risk tagging...

| Code | Label | Target |
| ----- | ----- | ----- |
| crime | Crime | yes |
| crime.fraud | Fraud | yes |
| crime.cyber | Cybercrime |  |
| crime.fin | Financial crime | yes |
| crime.env | Environmental violations |  |
| crime.theft | Theft | yes |
| crime.war | War crimes | yes |
| crime.boss | Criminal leadership | yes |
| crime.terror | Terrorism | yes |
| crime.traffick | Trafficking | yes |
| crime.traffick.drug | Drug trafficking |  |
| crime.traffick.human | Human trafficking |  |
| forced.labor | Forced labor |  |
| asset.frozen | Frozen asset |  |
| wanted | Wanted | yes |
| corp.offshore | Offshore |  |
| corp.shell | Shell company |  |
| corp.public | Public listed company |  |
| corp.disqual | Disqualified | yes |
| gov | Government |  |
| gov.national | National government |  |
| gov.state | State government |  |
| gov.muni | Municipal government |  |
| gov.soe | State-owned enterprise |  |
| gov.igo | Intergovernmental organization |  |
| gov.head | Head of government or state |  |
| gov.admin | Civil service |  |
| gov.executive | Executive branch of government |  |
| gov.legislative | Legislative branch of government |  |
| gov.judicial | Judicial branch of government |  |
| gov.security | Security services |  |
| gov.financial | Central banking and financial integrity |  |
| fin | Financial services |  |
| fin.bank | Bank |  |
| fin.fund | Fund |  |
| fin.adivsor | Financial advisor |  |
| reg.action | Regulator action | yes |
| reg.warn | Regulator warning | yes |
| role.pep | Politician | yes |
| role.pol | Non-PEP |  |
| role.rca | Close Associate | yes |
| role.judge | Judge |  |
| role.civil | Civil servant |  |
| role.diplo | Diplomat |  |
| role.lawyer | Lawyer |  |
| role.acct | Accountant |  |
| role.spy | Spy |  |
| role.oligarch | Oligarch | yes |
| role.journo | Journalist |  |
| role.act | Activist |  |
| role.lobby | Lobbyist |  |
| pol.party | Political party |  |
| pol.union | Union |  |
| rel | Religion |  |
| mil | Military |  |
| sanction | Sanctioned entity | yes |
| sanction.linked | Sanction-linked entity | yes |
| sanction.counter | Counter-sanctioned entity | yes |
| export.control | Export controlled | yes |
| export.risk | Trade risk | yes |
| debarment | Debarred entity | yes |
| poi | Person of interest | yes |

### **Dates**

Dates are given in a basic ISO 8601 date or date-time format,YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS. In source data, we find varying degrees of precision: some events may be defined as a full timestamp (2021-08-25T09:26:11), while for many we only know a year (2021) or month (2021-08). Such date prefixes are carried through and used to specify date precision as well as the actual value.

### **Countries**

We use a descriptive approach to modeling the territories referenced in our database. If a list refers to a country, so do we. If a territory has a government, we want to track that. This can, at times, lead to controversial political realities being expressed in our data structure, and a model of the world where multiple jurisdictions apply to the same physical territory.

As such, we use ISO 3166-1 alpha-2 as a starting point, but have also included countries that have ceased to exist (e.g. Soviet Union, Yugoslavia) and territories whose status as a country is controversial (e.g. Kosovo, Artsakh). In some cases, most commonly in the case of occupied territories, a country's jurisdiction is applied outside its internationally recognized borders. In these cases, we err on the side of accurately representing the jurisdiction rather than which country's borders a place is located in.

If the presence of a country in this list is offensive to you, we invite you to reflect on the mental health impact of being angry at tables on the internet.

| Code | Label |
| ----- | ----- |
| ac | Ascension Island |
| ad | Andorra |
| ae | United Arab Emirates |
| af | Afghanistan |
| ag | Antigua and Barbuda |
| ai | Anguilla |
| al | Albania |
| am | Armenia |
| ao | Angola |
| aq | Antarctica |
| ar | Argentina |
| as | American Samoa |
| at | Austria |
| au | Australia |
| aw | Aruba |
| ax | Åland Islands |
| az | Azerbaijan |
| az-nk | Artsakh |
| ba | Bosnia and Herzegovina |
| bb | Barbados |
| bd | Bangladesh |
| be | Belgium |
| bf | Burkina Faso |
| bg | Bulgaria |
| bh | Bahrain |
| bi | Burundi |
| bj | Benin |
| bl | Saint Barthélemy |
| bm | Bermuda |
| bn | Brunei |
| bo | Bolivia |
| bq | Bonaire, Sint Eustatius and Saba |
| br | Brazil |
| bs | Bahamas |
| bt | Bhutan |
| bv | Bouvet Island |
| bw | Botswana |
| by | Belarus |
| bz | Belize |
| ca | Canada |
| cc | Cocos (Keeling) Islands |
| cd | DR Congo |
| cf | Central African Republic |
| cg | Congo-Brazzaville |
| ch | Switzerland |
| ci | Côte d'Ivoire |
| ck | Cook Islands |
| cl | Chile |
| cm | Cameroon |
| cn | China |
| cn-xz | Tibet |
| co | Colombia |
| cp | Clipperton Island |
| cq | Sark |
| cr | Costa Rica |
| cshh | Czechoslovakia |
| csxx | Serbia and Montenegro |
| cu | Cuba |
| cv | Cape Verde |
| cw | Curaçao |
| cx | Christmas Island |
| cy | Cyprus |
| cy-trnc | Northern Cyprus |
| cz | Czechia |
| dd | East Germany |
| de | Germany |
| dg | Diego Garcia |
| dj | Djibouti |
| dk | Denmark |
| dm | Dominica |
| do | Dominican Republic |
| dz | Algeria |
| ec | Ecuador |
| ee | Estonia |
| eg | Egypt |
| eh | Western Sahara |
| er | Eritrea |
| es | Spain |
| et | Ethiopia |
| eu | European Union |
| fi | Finland |
| fj | Fiji |
| fk | Falkland Islands |
| fm | Micronesia |
| fo | Faroe Islands |
| fr | France |
| ga | Gabon |
| gb | United Kingdom |
| gb-nir | Northern Ireland |
| gb-sct | Scotland |
| gb-wls | Wales |
| gd | Grenada |
| ge | Georgia |
| ge-ab | Abkhazia (Occupied Georgia) |
| gf | French Guiana |
| gg | Guernsey |
| gh | Ghana |
| gi | Gibraltar |
| gl | Greenland |
| gm | Gambia |
| gn | Guinea |
| gp | Guadeloupe |
| gq | Equatorial Guinea |
| gr | Greece |
| gs | South Georgia and the South Sandwich Islands |
| gt | Guatemala |
| gu | Guam |
| gw | Guinea-Bissau |
| gy | Guyana |
| hk | Hong Kong SAR |
| hm | Heard and McDonald Islands |
| hn | Honduras |
| hr | Croatia |
| ht | Haiti |
| hu | Hungary |
| ic | Canary Islands |
| id | Indonesia |
| ie | Ireland |
| il | Israel |
| im | Isle of Man |
| in | India |
| io | British Indian Ocean Territory |
| iq | Iraq |
| iq-kr | Kurdistan |
| ir | Iran |
| is | Iceland |
| it | Italy |
| je | Jersey |
| jm | Jamaica |
| jo | Jordan |
| jp | Japan |
| ke | Kenya |
| kg | Kyrgyzstan |
| kh | Cambodia |
| ki | Kiribati |
| km | Comoros |
| kn | Saint Kitts and Nevis |
| kp | North Korea |
| kr | South Korea |
| kw | Kuwait |
| ky | Cayman Islands |
| kz | Kazakhstan |
| la | Laos |
| lb | Lebanon |
| lc | Saint Lucia |
| li | Liechtenstein |
| lk | Sri Lanka |
| lr | Liberia |
| ls | Lesotho |
| lt | Lithuania |
| lu | Luxembourg |
| lv | Latvia |
| ly | Libya |
| ma | Morocco |
| mc | Monaco |
| md | Moldova |
| md-pmr | Transnistria (PMR) |
| me | Montenegro |
| mf | Saint Martin |
| mg | Madagascar |
| mh | Marshall Islands |
| mk | North Macedonia |
| ml | Mali |
| mm | Myanmar |
| mn | Mongolia |
| mo | Macao SAR |
| mp | Northern Mariana Islands |
| mq | Martinique |
| mr | Mauritania |
| ms | Montserrat |
| mt | Malta |
| mu | Mauritius |
| mv | Maldives |
| mw | Malawi |
| mx | Mexico |
| my | Malaysia |
| mz | Mozambique |
| na | Namibia |
| nc | New Caledonia |
| ne | Niger |
| nf | Norfolk Island |
| ng | Nigeria |
| ni | Nicaragua |
| nl | Netherlands |
| no | Norway |
| np | Nepal |
| nr | Nauru |
| nu | Niue |
| nz | New Zealand |
| om | Oman |
| pa | Panama |
| pe | Peru |
| pf | French Polynesia |
| pg | Papua New Guinea |
| ph | Philippines |
| pk | Pakistan |
| pk-km | Kashmir |
| pl | Poland |
| pm | Saint Pierre and Miquelon |
| pn | Pitcairn |
| pr | Puerto Rico |
| ps | Palestinian territories |
| pt | Portugal |
| pw | Palau |
| py | Paraguay |
| qa | Qatar |
| re | Réunion |
| ro | Romania |
| rs | Serbia |
| ru | Russia |
| rw | Rwanda |
| sa | Saudi Arabia |
| sb | Solomon Islands |
| sc | Seychelles |
| sd | Sudan |
| se | Sweden |
| sg | Singapore |
| sh | Saint Helena, Ascension and Tristan da Cunha |
| si | Slovenia |
| sj | Svalbard and Jan Mayen |
| sk | Slovakia |
| sl | Sierra Leone |
| sm | San Marino |
| sn | Senegal |
| so | Somalia |
| so-som | Somaliland |
| sr | Suriname |
| ss | South Sudan |
| st | São Tomé and Príncipe |
| suhh | Soviet Union |
| sv | El Salvador |
| sx | Sint Maarten |
| sy | Syria |
| sz | Eswatini |
| ta | Tristan da Cunha |
| tc | Turks and Caicos Islands |
| td | Chad |
| tf | French Southern Territories |
| tg | Togo |
| th | Thailand |
| tj | Tajikistan |
| tk | Tokelau |
| tl | Timor-Leste |
| tm | Turkmenistan |
| tn | Tunisia |
| to | Tonga |
| tr | Türkiye |
| tt | Trinidad and Tobago |
| tv | Tuvalu |
| tw | Taiwan |
| tz | Tanzania |
| ua | Ukraine |
| ua-cri | Crimea (Occupied Ukraine) |
| ua-dpr | Donetsk (Occupied Ukraine) |
| ua-lpr | Luhansk (Occupied Ukraine) |
| ug | Uganda |
| um | U.S. Outlying Islands |
| un | United Nations |
| us | United States of America |
| uy | Uruguay |
| uz | Uzbekistan |
| va | Holy See |
| vc | Saint Vincent and the Grenadines |
| ve | Venezuela |
| vg | British Virgin Islands |
| vi | U.S. Virgin Islands |
| vn | Vietnam |
| vu | Vanuatu |
| wf | Wallis and Futuna |
| ws | Samoa |
| x-so | South Ossetia (Occupied Georgia) |
| xk | Kosovo |
| ye | Yemen |
| yt | Mayotte |
| yucs | Yugoslavia |
| za | South Africa |
| zm | Zambia |
| zr | Zaire |
| zw | Zimbabwe |
| zz | Global |

