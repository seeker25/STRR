import { z } from 'zod'
import type { Contact, PlatformContact } from '#imports'
import {
  optionalOrEmptyString, getRequiredEmail, getRequiredNonEmptyString, getRequiredPhone
} from '~/utils/connect-validation'

export const useStrrPlatformContact = defineStore('strr/platformContact', () => {
  const { t } = useI18n()
  const { userFullName } = storeToRefs(useConnectAccountStore())
  const getContactSchema = (completingParty = false) => {
    return z.object({
      firstName: getRequiredNonEmptyString(t('validation.name.first')),
      middleName: optionalOrEmptyString,
      lastName: getRequiredNonEmptyString(t('validation.name.last')),
      position: completingParty ? optionalOrEmptyString : getRequiredNonEmptyString(t('validation.position')),
      phone: getRequiredPhone(t('validation.required'), t('validation.phone.number')),
      faxNumber: optionalOrEmptyString,
      emailAddress: getRequiredEmail(t('validation.email'))
    })
  }

  const getUserNameChunks = () => {
    let firstName = ''
    let lastName = ''
    const nameChunks = userFullName.value.split(' ')
    if (nameChunks.length > 0) {
      firstName = nameChunks[0] as string
    }
    for (let i = 0; i < nameChunks.length; i++) {
      if (i === 0) {
        firstName = nameChunks[i] as string
      } else {
        // add other name chunks as last name
        lastName += ' ' + nameChunks[i] as string
      }
    }
    return {
      firstName,
      lastName
    }
  }

  const getNewContact = (isActiveUser = false): Contact => {
    const { firstName, lastName } = getUserNameChunks()
    return {
      firstName: isActiveUser ? firstName : '',
      middleName: '',
      lastName: isActiveUser ? lastName : '',
      phone: {
        countryIso2: '',
        countryCode: '',
        number: '',
        extension: ''
      },
      faxNumber: '',
      emailAddress: ''
    }
  }

  const completingParty = ref<Contact>(getNewContact(true))

  const getNewRepresentative = (isActiveUser = false): PlatformContact => {
    let contact = getNewContact(false)
    if (isActiveUser) {
      contact = JSON.parse(JSON.stringify(completingParty.value))
    }
    return {
      ...contact,
      position: ''
    }
  }

  const isCompletingPartyRep = ref<boolean | undefined>(undefined)
  const primaryRep = ref<PlatformContact | undefined>(undefined)
  watch(primaryRep, (val) => {
    if (val && isCompletingPartyRep.value) {
      completingParty.value.emailAddress = val?.emailAddress
      completingParty.value.phone = val?.phone
    }
  }, { deep: true })

  const secondaryRep = ref<PlatformContact | undefined>(undefined)

  return {
    completingParty,
    isCompletingPartyRep,
    primaryRep,
    secondaryRep,
    getContactSchema,
    getNewContact,
    getNewRepresentative
  }
})