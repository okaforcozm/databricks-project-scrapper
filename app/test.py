import datetime

req_payload = {
  "messageHeader": {
    "messageID": "d559a7c1-784d-49f7-a58c-818c77afc2bd",
    "conversationID": "agpzfnRyYWRlb3Mxch0LEhBjb21tZXJjZURvY3MvUkZRGICA6uSotvYIDA"
  },
  "businessInfo": {

  },
  "quotes": [
    {
      "referenceID": "agpzfnRyYWRlb3MxclQLEhJDaGFubmVsTWVzc2FnZVRlbXAiPGFncHpmblJ5WVdSbGIzTXhjaDBMRWhCamIyMXRaWEpqWlVSdlkzTXZVa1pSR0lDQTZ1U290dllJREEjMgw|2ea43c98-943f-4556-8e91-23513125e918",
      "businessInfo": {
        "parties": [
          {
            "partyTypeCode": "FW",
            "name": "Haulable",
            "ID": "agpzfnRyYWRlb3Mxch0LEhB1c2VyL0xlZ2FsRW50aXR5GICAkv-5hr4LDA"
          },
          {
            "partyTypeCode": "CB",
            "name": "Clearit|USA",
            "ID": "agpzfnRyYWRlb3MxcisLEh51c2VyL1RoaXJkUGFydHlTZXJ2aWNlUHJvdmlkZXIYgIDc192evAsM"
          },
          {
            "partyTypeCode": "IN",
            "name": "xcover.com",
            "ID": "agpzfnRyYWRlb3MxcisLEh51c2VyL1RoaXJkUGFydHlTZXJ2aWNlUHJvdmlkZXIYgID8_6O1yQgM"
          }
        ]
      },
      "transportMode": "FCL",
      "transportService": "Port-to-port",
      "connection": {
        "transitTime": {
          "estimatedTransitTimes": [
            {
              "from": {
                "value": 13,
                "unitCode": "DAY"
              },
              "to": {
                "value": 18,
                "unitCode": "DAY"
              }
            }
          ]
        },
        "generalCharges": [
          {
            "feeType": "customsBrokerage",
            "feeCode": "ENTF_3RD",
            "feeName": "Import Customs Clearance",
            "quantity": 1,
            "unitRate": {
              "value": 125,
              "currencyID": "USD"
            },
            "rate": {
              "value": 92.89,
              "currencyID": "GBP"
            }
          },
          {
            "feeType": "customsBrokerage",
            "feeCode": "ISF_FEE_3RD",
            "feeName": "ISF Fee",
            "quantity": 1,
            "unitRate": {
              "value": 50,
              "currencyID": "USD"
            },
            "rate": {
              "value": 37.16,
              "currencyID": "GBP"
            }
          },
          {
            "feeType": "customsBrokerage",
            "feeCode": "SEB_3RD",
            "feeName": "Single Entry Bond",
            "feeComment": "Note: Your booking's combined duties, taxes, and goods value is covered up to $10,000. Any value exceeding $10,000 will incur a 0.65% surcharge.",
            "quantity": 1,
            "unitRate": {
              "value": 65,
              "currencyID": "USD"
            },
            "rate": {
              "value": 48.3,
              "currencyID": "GBP"
            }
          },
          {
            "feeType": "customsBrokerage",
            "feeCode": "ISF_3RD",
            "feeName": "ISF Bond",
            "quantity": 1,
            "unitRate": {
              "value": 75,
              "currencyID": "USD"
            },
            "rate": {
              "value": 55.73,
              "currencyID": "GBP"
            }
          },
          {
            "feeType": "insurance",
            "feeCode": "XCover Transport Insurance",
            "feeName": "Transport Insurance",
            "quantity": 1,
            "unitRate": {
              "value": 57.03,
              "currencyID": "USD"
            },
            "rate": {
              "value": 42.38,
              "currencyID": "GBP"
            }
          },
          {
            "feeType": "platform",
            "feeCode": "PLF",
            "feeName": "Freightos platform fee",
            "rate": {
              "value": 26.54,
              "currencyID": "GBP"
            }
          }
        ],
        "connectionSegments": [
          {
            "segmentID": "1",
            "transportMode": "FCL",
            "legs": [
              {
                "origin": {
                  "locationTypeCode": "Seaport",
                  "locationCode": "GBLON",
                  "countryID": {
                    "value": "GB"
                  }
                },
                "destination": {
                  "locationTypeCode": "Seaport",
                  "locationCode": "USNYC",
                  "countryID": {
                    "value": "US"
                  }
                }
              }
            ],
            "charges": [
              {
                "feeType": "origin",
                "feeCode": "O-LOCAL",
                "feeName": "Local Charges at Origin",
                "feeComment": "Included",
                "quantity": 1,
                "unitRate": {
                  "value": 0,
                  "currencyID": "USD"
                },
                "rate": {
                  "value": 0,
                  "currencyID": "GBP"
                }
              },
              {
                "feeType": "service",
                "feeCode": "Ocean",
                "feeName": "Ocean Freight Cost",
                "quantity": 1,
                "unitRate": {
                  "value": 1493,
                  "currencyID": "GBP"
                },
                "rate": {
                  "value": 1493,
                  "currencyID": "GBP"
                }
              },
              {
                "feeType": "destination",
                "feeCode": "D-LOCAL",
                "feeName": "Local Charges at Destination",
                "feeComment": "Included",
                "quantity": 1,
                "unitRate": {
                  "value": 0,
                  "currencyID": "USD"
                },
                "rate": {
                  "value": 0,
                  "currencyID": "GBP"
                }
              }
            ],
            "availableSpace": {
              "guaranteedSpace": False
            }
          }
        ]
      },
      "originLocation": {
        "locationTypeCode": "Seaport",
        "locationCode": "GBLON",
        "countryID": {
          "value": "GB"
        }
      },
      "destinationLocation": {
        "locationTypeCode": "Seaport",
        "locationCode": "USNYC",
        "countryID": {
          "value": "US"
        }
      },
      "nearBy": False,
      "createDate": "2025-06-21T15:04:12.926Z",
      "quoteURIReference": {
        "uri": "https://integration.freightos.com/marketplace/booking/sites/ship/quotes/agpzfnRyYWRlb3MxclQLEhJDaGFubmVsTWVzc2FnZVRlbXAiPGFncHpmblJ5WVdSbGIzTXhjaDBMRWhCamIyMXRaWEpqWlVSdlkzTXZVa1pSR0lDQTZ1U290dllJREEjMgw%7C2ea43c98-943f-4556-8e91-23513125e918/confirm?x-token=9VgkBGGzdQUgReRU2wGuLeOjgcY",
        "validTo": "2025-06-21T16:49:12.926Z"
      },
      "validTo": "2025-06-30T23:59:59.000Z",
      "insurance": {
        "insuranceValueAmount": {
          "value": 9000,
          "currencyID": "USD"
        }
      },
      "declaredCustomsValueAmount": {
        "value": 9000,
        "currencyID": "USD"
      },
      "priceIndicator": {
        "exchangeRates": [
          {
            "from": {
              "value": "USD"
            },
            "to": {
              "value": "GBP"
            },
            "exchangeRate": 0.7431
          }
        ],
        "includeOriginPortCharges": True,
        "includeDestinationPortCharges": True,
        "totalCharge": {
          "value": 1796,
          "currencyID": "GBP"
        },
        "totalChargeDiscounted": {
          "value": 1796,
          "currencyID": "GBP"
        }
      },
      "remarks": {
        "value": "\u003Cb\u003EQuote ID:\u003C/b\u003E 9668175\u003Cbr /\u003E\u003Cb\u003EService name:\u003C/b\u003E Haulable International - Port to Port\u003Cbr\u003E\u003Cb\u003EQuote Id:\u003C/b\u003E 0503465f-b21d-43cf-a761-7b92601f37530\u003Cbr\u003E\u003Cb\u003EQuote Ref:\u003C/b\u003E KQ92EYPK0\u003Cbr\u003E\u003Cb\u003EValid To:\u003C/b\u003E 30 June 2025 23:59 GMT\u003Cbr\u003EAll rates subject to space at time of booking and are based on cargo that is suitably packed for shipment. All quotes are subject to BIFA 2017 terms and conditions of trading.\u003Cbr\u003EAll prices quoted are on standard delivery, timed/weekend delivery incur additional charges.\u003Cbr\u003EQuotations are based on commercial general cargo. Not valid for special cargo, such as alcohol, batteries, PPE etc or for moves to/from a private individual and/or private address.\u003Cbr\u003EQuotations are based on non-hazardous, stackable cargo, and are subject to the right of withdrawal or revision by the company.\u003Cbr\u003E\u003Cbr\u003EQuotations exclude all import duties and taxes, deferment fees, customs examinations, inspections fees, secondary screening costs and where applicable hazardous fees, storage fees, demurrage, fumigation, and special requirements at collection / delivery fees except where stated.\u003Cbr\u003E\u003Cbr\u003ERates exclude supplier licencing which may be applicable depending on the commodity. Haulable is able to assist factories with this at the time of booking should they be required. An additional USD 130 will be charged for Simplified licences and USD 220 or more for other commodity licences.\u003Cbr\u003EAll business of the Company is transacted under the current edition of the Standard Trading Conditions of the British International Freight Association which are available on request.\u003Cbr\u003E\u003Cbr\u003E\u003Cb\u003ESurcharges:\u003C/b\u003E\u003Cbr\u003EDuties and taxes paid on your behalf will incur a 1.5% / GBP25 Min handling charge.\u003Cbr\u003ECustoms Entries include up to three lines on a single-entry, additional lines are charged at GBP2.50 per line.\u003Cbr\u003E\u003Cbr\u003EFor single lift pieces 1000 kg or over for transhipment ports need to be checked with office for appropriate offloading equipment.\u003Cbr\u003E\u003Cbr\u003EIf original BOL’s are required postage or a courier can be arranged upon request.\u003Cbr\u003EHaulable Ltd, reserves the right to refuse or revise any quotation if cargo is deemed not suitable for LCL shipment. Non stackable, heavy items (over 2500 kgs) or items over 4.5 metres in length may be subject to additional charges and residential collections and deliveries.\u003Cbr\u003E\u003Cbr\u003EAdditional services: AM/PM pickup or delivery will be charged at GBP 25.00.\u003Cbr\u003E\u003Cb style=\"font-family: Slack-Lato, appleLogo, sans-serif; font-size: 15px; box-sizing: inherit; color: rgb(29, 28, 29); font-variant-ligatures: common-ligatures; background-color: rgb(255, 255, 255);\"\u003E\u003Cu\u003EClearit Customs Brokerage Services\u003C/u\u003E\u003C/b\u003E\u003Cbr style=\"box-sizing: inherit; color: rgb(29, 28, 29); font-family: Slack-Lato, appleLogo, sans-serif; font-size: 15px; font-variant-ligatures: common-ligatures; background-color: rgb(255, 255, 255);\"\u003E\u003Cspan style=\"font-family: Slack-Lato, appleLogo, sans-serif; font-size: 15px; color: rgb(29, 28, 29); font-variant-ligatures: common-ligatures; background-color: rgb(255, 255, 255);\"\u003E\u003Cb\u003EUS Import Customs Clearance includes:\u003C/b\u003E\u003C/span\u003E\u003Cbr style=\"box-sizing: inherit; color: rgb(29, 28, 29); font-family: Slack-Lato, appleLogo, sans-serif; font-size: 15px; font-variant-ligatures: common-ligatures; background-color: rgb(255, 255, 255);\"\u003E\u003Cspan style=\"font-family: Slack-Lato, appleLogo, sans-serif; font-size: 15px; color: rgb(29, 28, 29); font-variant-ligatures: common-ligatures; background-color: rgb(255, 255, 255);\"\u003EImporter activation, CCI review, ACE cargo release, Duty and tax computation, ABI processing, ACE entry summary, Preparation of duty payment, Liquidation monitoring, Shipment event tracking, Status notification, Entry data archiving.\u003C/span\u003E\u003Cspan class=\"c-mrkdwn__br\" style=\"font-family: Slack-Lato, appleLogo, sans-serif; font-size: 15px; box-sizing: inherit; display: block; height: 8px; color: rgb(29, 28, 29); font-variant-ligatures: common-ligatures; background-color: rgb(255, 255, 255);\"\u003E\u003C/span\u003E\u003Cspan style=\"font-family: Slack-Lato, appleLogo, sans-serif; font-size: 15px; color: rgb(29, 28, 29); font-variant-ligatures: common-ligatures; background-color: rgb(255, 255, 255);\"\u003E\u003Cbr\u003E\u003Cb\u003EOther Charges that may apply:\u003C/b\u003E\u003C/span\u003E\u003Cbr style=\"box-sizing: inherit; color: rgb(29, 28, 29); font-family: Slack-Lato, appleLogo, sans-serif; font-size: 15px; font-variant-ligatures: common-ligatures; background-color: rgb(255, 255, 255);\"\u003E\u003Cspan style=\"background-color: rgb(255, 255, 255);\"\u003E\u003Cfont color=\"#1d1c1d\"\u003E\u003Cspan style=\"font-size: 15px; font-variant-ligatures: common-ligatures;\"\u003E• Additional invoice lines (after 5): 2.50 USD per line\u003C/span\u003E\u003C/font\u003E\u003C/span\u003E\u003Cbr style=\"box-sizing: inherit; color: rgb(29, 28, 29); font-family: Slack-Lato, appleLogo, sans-serif; font-size: 15px; font-variant-ligatures: common-ligatures; background-color: rgb(255, 255, 255);\"\u003E\u003Cspan style=\"background-color: rgb(255, 255, 255);\"\u003E\u003Cfont color=\"#1d1c1d\"\u003E\u003Cspan style=\"font-size: 15px; font-variant-ligatures: common-ligatures;\"\u003E• Partner Government Agency (PGA) Declaration: 35 USD\u003C/span\u003E\u003C/font\u003E\u003C/span\u003E\u003Cbr style=\"box-sizing: inherit; color: rgb(29, 28, 29); font-family: Slack-Lato, appleLogo, sans-serif; font-size: 15px; font-variant-ligatures: common-ligatures; background-color: rgb(255, 255, 255);\"\u003E\u003Cspan style=\"background-color: rgb(255, 255, 255);\"\u003E\u003Cfont color=\"#1d1c1d\"\u003E\u003Cspan style=\"font-size: 15px; font-variant-ligatures: common-ligatures;\"\u003E• HTS code classification (after 2): 10 USD each\u003C/span\u003E\u003C/font\u003E\u003C/span\u003E\u003Cbr style=\"box-sizing: inherit; color: rgb(29, 28, 29); font-family: Slack-Lato, appleLogo, sans-serif; font-size: 15px; font-variant-ligatures: common-ligatures; background-color: rgb(255, 255, 255);\"\u003E\u003Cspan style=\"background-color: rgb(255, 255, 255);\"\u003E\u003Cfont color=\"#1d1c1d\"\u003E\u003Cspan style=\"font-size: 15px; font-variant-ligatures: common-ligatures;\"\u003E• Prior notice: 35 USD\u003C/span\u003E\u003C/font\u003E\u003C/span\u003E\u003Cbr style=\"box-sizing: inherit; color: rgb(29, 28, 29); font-family: Slack-Lato, appleLogo, sans-serif; font-size: 15px; font-variant-ligatures: common-ligatures; background-color: rgb(255, 255, 255);\"\u003E\u003Cspan style=\"background-color: rgb(255, 255, 255);\"\u003E\u003Cfont color=\"#1d1c1d\"\u003E\u003Cspan style=\"font-size: 15px; font-variant-ligatures: common-ligatures;\"\u003E• A 5% Disbursement fee will be added when paying duties and taxes by credit card.\u003C/span\u003E\u003C/font\u003E\u003C/span\u003E\u003Cdiv style=\"font-family: &quot;Open sans&quot;, sans-serif, Arial; font-size: 11pt;\"\u003E• Additional Single Entry Bond fee for shipments requiring and Partner Government Agencies (FDA, EPA, USDA, etc.) as it requires a tripling (3x) of the invoice value in order to calculate the bond requirements.\u003C/div\u003E\u003Cdiv style=\"font-family: &quot;Open sans&quot;, sans-serif, Arial; font-size: 11pt;\"\u003E\u003Cfont\u003E\u003Cspan style=\"font-size: 14.6667px;\"\u003E\u003Cbr\u003E\u003C/span\u003E\u003C/font\u003E\u003C/div\u003E\u003Cdiv style=\"font-family: &quot;Open sans&quot;, sans-serif, Arial; font-size: 11pt;\"\u003E\u003Cfont\u003E\u003Cspan style=\"font-size: 14.6667px;\"\u003ECustoms Duties &amp; Import Bond fees are not included in this quote.\u003C/span\u003E\u003C/font\u003E\u003Cbr\u003E\u003Cspan class=\"c-mrkdwn__br\" style=\"font-family: Slack-Lato, appleLogo, sans-serif; font-size: 15px; box-sizing: inherit; display: block; height: 8px; color: rgb(29, 28, 29); font-variant-ligatures: common-ligatures; background-color: rgb(255, 255, 255);\"\u003E\u003Cbr\u003E\u003C/span\u003E\u003Cspan style=\"font-family: Slack-Lato, appleLogo, sans-serif; font-size: 15px; color: rgb(29, 28, 29); font-variant-ligatures: common-ligatures; background-color: rgb(255, 255, 255);\"\u003EQuotations provided by Clearit including duties/taxes are for information purposes only and are subject to change without notice; No quotation shall be binding.\u003C/span\u003E\u003Cspan class=\"c-mrkdwn__br\" style=\"font-family: Slack-Lato, appleLogo, sans-serif; font-size: 15px; box-sizing: inherit; display: block; height: 8px; color: rgb(29, 28, 29); font-variant-ligatures: common-ligatures; background-color: rgb(255, 255, 255);\"\u003E\u003C/span\u003E\u003Cspan style=\"font-family: Slack-Lato, appleLogo, sans-serif; font-size: 15px; color: rgb(29, 28, 29); font-variant-ligatures: common-ligatures; background-color: rgb(255, 255, 255);\"\u003EThe&nbsp;Customer acknowledges that it is required to review all documents and declarations prepared and/or filed with the U.S. Customs &amp; Border Protection, other Government Agencies and/or Third Parties, and will immediately advise the Company of any errors, discrepancies, incorrect statements, or omissions on any declaration or other submission filed on the Customers behalf;\u003C/span\u003E\u003C/div\u003E\u003Cdiv style=\"font-family: &quot;Open sans&quot;, sans-serif, Arial; font-size: 11pt;\"\u003E\u003Cbr style=\"box-sizing: inherit; color: rgb(29, 28, 29); font-family: Slack-Lato, appleLogo, sans-serif; font-size: 15px; font-variant-ligatures: common-ligatures; background-color: rgb(255, 255, 255);\"\u003E\u003Cspan style=\"font-family: Slack-Lato, appleLogo, sans-serif; font-size: 15px; color: rgb(29, 28, 29); font-variant-ligatures: common-ligatures; background-color: rgb(255, 255, 255);\"\u003ECustomers shall use reasonable care to ensure the correctness of all such information and shall indemnify and hold the Company harmless from any and all claims asserted and/or liability or losses suffered by reason of the Customers failure to disclose information or any incorrect, incomplete or false&nbsp;statement&nbsp;by the Customer or its agent, representative or contractor upon which Clearit reasonably relied. The Customer agrees that the Customer has an affirmative non-delegable duty to disclose any and all information required to import, export, or enter the goods.\u003C/span\u003E\u003C/div\u003E\u003Cbr\u003E\u003Cbr\u003E\u003Cdiv class=\"c-message_kit__gutter\" style=\"box-sizing: inherit; display: flex; padding: 8px 20px 8px 12px; color: rgb(29, 28, 29); font-family: Slack-Lato, appleLogo, sans-serif; font-size: 15px; font-variant-ligatures: common-ligatures; background-color: rgb(248, 248, 248);\"\u003E\u003Cdiv class=\"c-message_kit__gutter__right\" style=\"box-sizing: inherit; flex: 1 1 0px; min-width: 0px; padding: 8px 0px 8px 16px; margin: -12px -8px -16px -16px;\"\u003E\u003Cdiv class=\"c-message_kit__blocks c-message_kit__blocks--rich_text\" style=\"box-sizing: inherit; max-width: none; margin-bottom: 4px;\"\u003E\u003Cdiv class=\"c-message__message_blocks c-message__message_blocks--rich_text\" style=\"box-sizing: inherit; max-width: none; overflow-wrap: break-word;\"\u003E\u003Cdiv class=\"p-block_kit_renderer\" style=\"box-sizing: inherit; width: 1114px;\"\u003E\u003Cdiv class=\"p-block_kit_renderer__block_wrapper p-block_kit_renderer__block_wrapper--first\" style=\"box-sizing: inherit; display: flex;\"\u003E\u003Cdiv class=\"p-rich_text_block\" style=\"box-sizing: inherit; counter-reset: list-0 0 list-1 0 list-2 0 list-3 0 list-4 0 list-5 0 list-6 0 list-7 0 list-8 0 list-9 0; width: 1114px; user-select: text; line-height: 1.46668;\"\u003E\u003Cdiv class=\"p-rich_text_section\" style=\"box-sizing: inherit; counter-reset: list-0 0 list-1 0 list-2 0 list-3 0 list-4 0 list-5 0 list-6 0 list-7 0 list-8 0 list-9 0;\"\u003E\u003Cb\u003E\u003Cu\u003EXCover.com Insurance\u003C/u\u003E\u003C/b\u003E&nbsp;\u003C/div\u003E\u003Cdiv class=\"p-rich_text_section\" style=\"box-sizing: inherit; counter-reset: list-0 0 list-1 0 list-2 0 list-3 0 list-4 0 list-5 0 list-6 0 list-7 0 list-8 0 list-9 0;\"\u003E\u003Cspan style=\"box-sizing: inherit;\"\u003EView\u003C/span\u003E&nbsp;the terms of your insurance policy. By clicking on “Select” and choosing your preferred logistics provider for this shipment, you confirm that you have read and that you confirm that you have read and that you accept the terms of your insurance cover. Your insurance policy is underwritten by Berkley Insurance Company (Singapore Branch) and administered by Cover Genius Trading Pty. Ltd.&nbsp;\u003Ca target=\"_blank\" class=\"c-link\" href=\"http://xcover.com/\" rel=\"noopener noreferrer\" tabindex=\"-1\" style=\"box-sizing: inherit; text-decoration-line: none;\"\u003EXCover.com\u003C/a\u003E&nbsp;is a trading name of Cover Genius Trading Pty. Ltd.\u003C/div\u003E\u003C/div\u003E\u003C/div\u003E\u003C/div\u003E\u003C/div\u003E\u003C/div\u003E\u003C/div\u003E\u003C/div\u003E\u003Cdiv class=\"c-message_actions__container c-message__actions\" style=\"box-sizing: inherit; position: absolute; top: -16px; right: 17px; display: inline-flex; z-index: 1; color: rgb(29, 28, 29); font-family: Slack-Lato, appleLogo, sans-serif; font-size: 15px; font-variant-ligatures: common-ligatures; background-color: rgb(248, 248, 248);\"\u003E\u003Cdiv class=\"c-message_actions__group\" style=\"box-sizing: inherit; background: rgba(var(--sk_primary_background,255,255,255),1); line-height: 1; margin-left: 8px; border: unset; --saf-0:rgba(var(--sk_foreground_low,29,28,29),0.13); box-shadow: 0 0 0 1px var(--saf-0),0 1px 3px 0 rgba(0,0,0,0.08); display: flex; padding: 2px; border-radius: 0.375em;\"\u003E\u003C/div\u003E\u003C/div\u003E\u003Cbr\u003E"
      },
      "co2Emissions": {
        "value": 631,
        "unitCode": "kg"
      },
      "additionalInformation": [
        {
          "key": "cancellationPolicy",
          "value": "STANDARD"
        },
        {
          "key": "providerType",
          "value": "FREIGHT_FORWARDER"
        }
      ],
      "URIReferences": {
        "bookingConfirm": {
          "uri": "https://integration.freightos.com/marketplace/booking/sites/ship/quotes/agpzfnRyYWRlb3MxclQLEhJDaGFubmVsTWVzc2FnZVRlbXAiPGFncHpmblJ5WVdSbGIzTXhjaDBMRWhCamIyMXRaWEpqWlVSdlkzTXZVa1pSR0lDQTZ1U290dllJREEjMgw%7C2ea43c98-943f-4556-8e91-23513125e918/confirm?x-token=9VgkBGGzdQUgReRU2wGuLeOjgcY",
          "validTo": "2025-06-21T16:49:12.926Z"
        },
        "checkout": {
          "uri": "https://ship.freightos.com/book/agpzfnRyYWRlb3MxclQLEhJDaGFubmVsTWVzc2FnZVRlbXAiPGFncHpmblJ5WVdSbGIzTXhjaDBMRWhCamIyMXRaWEpqWlVSdlkzTXZVa1pSR0lDQTZ1U290dllJREEjMgw%7C2ea43c98-943f-4556-8e91-23513125e918?showMissingServices=false&auth=9VgkBGGzdQUgReRU2wGuLeOjgcY",
          "validTo": "2025-06-21T16:49:12.926Z"
        }
      }
    }
  ],
  "paging": {
    "hasMore": False,
    "count": 1
  },
  "URIReferences": {
    "results": {
      "uri": "https://ship.freightos.com/results/agpzfnRyYWRlb3Mxch0LEhBjb21tZXJjZURvY3MvUkZRGICA6uSotvYIDA"
    },
    "services": {
      "uri": "https://ship.freightos.com/search/services/agpzfnRyYWRlb3Mxch0LEhBjb21tZXJjZURvY3MvUkZRGICA6uSotvYIDA"
    }
  }
}

def locode_to_city_country(locode):
    # Basic decoding for UN/LOCODE: e.g., GBLON → city=London, country=GB
    if not locode or len(locode) < 5:
        return "", ""
    country = locode[:2]
    city = locode[2:]
    # Optionally, you can expand this to a full lookup dictionary
    LOCODE_CITIES = {
        "LON": "LONDON",
        "NYC": "NEW YORK",
        # Add more mappings as needed
    }
    return LOCODE_CITIES.get(city, city), country

def transform_freightos_response(data):
    quote = data["quotes"][0]
    # City/country from origin/destination location
    origin_code = quote.get("originLocation", {}).get("locationCode", "")
    dest_code = quote.get("destinationLocation", {}).get("locationCode", "")
    city_of_origin, country_of_origin = locode_to_city_country(origin_code)
    city_of_destination, country_of_destination = locode_to_city_country(dest_code)

    # Date of shipping: use createDate or fallback to today
    date_of_shipping = quote.get("createDate", datetime.date.today().isoformat())[:10]

    # Total shipping time: try from->value, then to->value, then None
    try:
        shipping_time = quote["connection"]["transitTime"]["estimatedTransitTimes"][0]["from"]["value"]
    except Exception:
        shipping_time = None

    # Price & currency: use priceIndicator.totalCharge if present, otherwise use segment charge
    price_info = quote.get("priceIndicator", {}).get("totalCharge", {})
    price_of_shipping = price_info.get("value", None)
    currency = price_info.get("currencyID", None)
    if price_of_shipping is None:
        # Fallback to first connection segment charge
        try:
            price_of_shipping = quote["connection"]["connectionSegments"][0]["charges"][0]["rate"]["value"]
            currency = quote["connection"]["connectionSegments"][0]["charges"][0]["rate"]["currencyID"]
        except Exception:
            price_of_shipping = None
            currency = None

    # Container type: try to infer from charge/unitRate/unit or transportMode
    container_type = quote.get("transportMode", "FCL")

    # Provider: first party with partyTypeCode == "FW"
    carrier = ""
    for party in quote.get("businessInfo", {}).get("parties", []):
        if party.get("partyTypeCode") == "FW":
            carrier = party.get("name", "")
            break

    # Carrier: often blank, can use provider or leave as ""
  

    # Shipment ID and rate ID: from referenceID if present
    shipment_id = quote.get("referenceID", "")
    rate_id = quote.get("connection", {}).get("connectionSegments", [{}])[0].get("segmentID", "")

    # CO2 data
    co2_amount = quote.get("co2Emissions", {}).get("value", 0)
    co2_price = None  # Not present in this payload

    # Validity
    validity_from = date_of_shipping
    validity_to = quote.get("validTo", "")

    # Distance, point_total, route_total: not present, set as None or ""
    distance = ""
    point_total = None
    route_total = None

    return {
        "city_of_origin": city_of_origin,
        "country_of_origin": country_of_origin,
        "city_of_destination": city_of_destination,
        "country_of_destination": country_of_destination,
        "date_of_shipping": date_of_shipping,
        "total_shipping_time_days": shipping_time,
        "price_of_shipping": price_of_shipping,
        "currency": currency,
        "container_type": container_type,
        "provider": "Freightos",
        "carrier": carrier,
        "shipment_id": shipment_id,
        "rate_id": rate_id,
        "co2_amount": co2_amount,
        "co2_price": co2_price,
        "validity_from": validity_from,
        "validity_to": validity_to,
        "distance": distance,
        "point_total": point_total,
        "route_total": route_total
    }


if __name__ == "__main__":
    transformed = transform_freightos_response(req_payload)
    print(transformed)
