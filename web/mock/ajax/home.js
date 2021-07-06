import chalk from 'chalk'

import { sleep } from './util'

export async function response (getArgs, postArgs, req) {
    console.log(chalk.cyan('req', req.method))
    console.log(chalk.cyan('getArgs', JSON.stringify(getArgs, null, 0)))
    console.log(chalk.cyan('postArgs', JSON.stringify(postArgs, null, 0)))
    console.log()

    const delay = getArgs.delay
    delay && await sleep(delay)

    const invoke = getArgs.invoke
    if (invoke === 'example') {
        return {
            code: 0,
            data: {
                text: 'Hello World!'
            },
            message: 'ok'
        }
    }
    return {
        code: 1,
        data: null,
        message: 'failed'
    }
}
