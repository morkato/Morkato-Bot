/**
 * /apt/bot/guilds/[id]/arts
 * 
 *   AllowedMethods: 
 *     
 *     >> GET
 *     >> POST
 */

import { allArts, forCreateArt } from 'middlewares/bot/art'
import { then } from 'middlewares/utils'
import { NextResponse } from 'next/server'

export const GET = then(allArts(async (req, { params }, { arts }) => NextResponse.json(arts)))
export const POST = then(forCreateArt(async (req, { params }, { art }) => NextResponse.json(art)))